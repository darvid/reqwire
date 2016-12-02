"""Helpers for managing Python package requirements."""
from __future__ import absolute_import

import enum
import html.parser
import optparse

import atomicwrites
import pip.basecommand
import pip.cmdoptions
import pip.download
import pip.models
import pip.req
import piptools.repositories
import piptools.resolver
import piptools.utils
import requests


MYPY = False
if MYPY:
    from typing import Any, Iterable, Optional, Set, Tuple  # noqa: F401

    IRequirementIter = Iterable[pip.req.InstallRequirement]
    IRequirementSet = Set[pip.req.InstallRequirement]


__all__ = (
    'build_ireq_set',
    'get_canonical_name',
    'parse_requirements',
    'resolve_ireqs',
    'resolve_specifier',
    'update_ireq_name',
    'write_requirements',
)


class PyPiHtmlParserState(enum.IntEnum):

    waiting = 0
    collecting_package_name = 1
    found_package_name = 2


class PyPiHtmlParser(html.parser.HTMLParser, object):

    def __init__(self, search=None, *args, **kwargs):
        super(PyPiHtmlParser, self).__init__(*args, **kwargs)
        self.search = search.lower() if search is not None else None
        self.state = PyPiHtmlParserState.waiting
        self.collected_packages = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.state = PyPiHtmlParserState.collecting_package_name

    def handle_endtag(self, tag):
        if (tag == 'a' and
                self.state == PyPiHtmlParserState.collecting_package_name):
            self.state = PyPiHtmlParserState.waiting

    def handle_data(self, data):
        if self.state == PyPiHtmlParserState.collecting_package_name:
            self.collected_packages.append(data)
            if self.search is not None and data.lower() == self.search:
                self.state = PyPiHtmlParserState.found_package_name


class _PipCommand(pip.basecommand.Command):

    name = '_PipCommand'


def build_ireq_set(specifiers,                    # type: Iterable[str]
                   index_urls=None,  # type: Optional[Iterable[str]]
                   resolve_canonical_names=True,  # type: bool
                   resolve_versions=True,         # type: bool
                   ):
    # type: (...) -> IRequirementSet
    """Builds a set of install requirements.

    Args:
        specifiers: A list of specifier strings.
        index_urls: List of Python package indexes. Only used if
            **resolve_canonical_names** or **resolve_versions** is
            ``True``.
        resolve_canonical_names: Queries package indexes provided by
            **index_urls** for the canonical name of each
            specifier. For example, *flask* will get resolved to
            *Flask*.
        resolve_versions: Queries package indexes for latest package
            versions.

    Returns:
        A set of :class:`pip.req.InstallRequirement`.

    """
    install_requirements = set()
    for specifier in specifiers:
        if resolve_versions:
            args = []
            for index_url in index_urls:
                args.extend(['--extra-index-url', index_url])
            ireq = resolve_specifier(specifier, False, *args)
        else:
            ireq = pip.req.InstallRequirement.from_line(specifier)
        if resolve_canonical_names:
            package_name = piptools.utils.name_from_req(ireq)
            canonical_name = get_canonical_name(
                package_name=package_name, index_urls=index_urls)
            update_ireq_name(
                install_requirement=ireq, package_name=canonical_name)
        install_requirements.add(ireq)
    return install_requirements


def build_pip_session(*args):
    # type: (str) -> Tuple[optparse.Values, pip.download.PipSession]
    pip_command = _PipCommand()
    index_opts = pip.cmdoptions.make_option_group(
        pip.cmdoptions.index_group,
        pip_command.parser,
    )
    pip_command.parser.insert_option_group(0, index_opts)
    pip_command.parser.add_option(optparse.Option(
        '--pre', action='store_true', default=False))
    pip_options, _ = pip_command.parse_args(list(args))
    session = pip_command._build_session(pip_options)
    return pip_options, session


def get_canonical_name(package_name, index_urls=None, *args):
    # type: (str, Optional[Iterable[str]], str) -> str
    """Returns the canonical name of the given Python package.

    Args:
        package_name: The package name.
        index_urls: A list of Python package indexes.
        *args: Command-line options and arguments passed to pip.

    """
    if not index_urls:
        index_urls = {pip.models.PyPI.simple_url}
    for index_url in index_urls:
        response = requests.get(index_url, stream=True)
        parser = PyPiHtmlParser(search=package_name)
        for line in response.iter_lines():
            parser.feed(line)
            if parser.state == PyPiHtmlParserState.found_package_name:
                parser.close()
                return parser.collected_packages[-1]
        parser.close()
    return package_name


def parse_requirements(filename, *args):
    # type: (str, str) -> Tuple[IRequirementSet, pip.index.PackageFinder]
    """Parses a requirements source file.

    Args:
        filename: The requirements source filename.
        *args: Command-line options and arguments passed to pip.

    Returns:
        A set of :class:`pip.req.InstallRequirement`, and a
        :class:`pip.index.PackageFinder` instance.

    """
    pip_options, session = build_pip_session(*args)
    repository = piptools.repositories.PyPIRepository(pip_options, session)
    requirements = pip.req.parse_requirements(
        filename,
        finder=repository.finder,
        session=repository.session,
        options=pip_options)
    return set(requirements), repository.finder


def resolve_ireqs(requirements,       # type: IRequirementIter
                  prereleases=False,  # type: bool
                  intersect=False,    # type: bool
                  *args,              # type: str
                  **kwargs            # type: Any
                  ):
    # type: (...) -> IRequirementSet
    """Resolves install requirements with piptools.

    Args:
        requirements: An iterable of :class:`pip.req.InstallRequirement`.
        prereleases: Whether or not to include prereleases.
        intersect: Return only install requirements that intersect with
            **requirements**. Default behavior is to include the entire
            dependency graph as produced by piptools.
        *args: Command-line options and arguments passed to pip.
        **kwargs: Passed to :class:`piptools.resolver.Resolver`.

    Returns:
        A set of :class:`pip.req.InstallRequirement`.

    """
    pip_options, session = build_pip_session(*args)
    repository = piptools.repositories.PyPIRepository(pip_options, session)
    resolver = piptools.resolver.Resolver(
        constraints=requirements, repository=repository, **kwargs)
    results = resolver.resolve()
    if intersect:
        results = {ireq for ireq in results
                   if ireq in set(requirements)}
    return results


def resolve_specifier(specifier, prereleases=False, *args):
    # type: (str, bool, str) -> pip.req.InstallRequirement
    """Resolves the given specifier.

    Args:
        specifier: A specifier string.
        prereleases: Whether or not to include prereleases.
        *args: Command-line options and arguments passed to pip.

    Returns:
        A set of :class:`pip.req.InstallRequirement`.

    """
    ireq = pip.req.InstallRequirement.from_line(specifier)
    pip_options, session = build_pip_session(*args)
    repository = piptools.repositories.PyPIRepository(pip_options, session)
    if ireq.editable or piptools.utils.is_pinned_requirement(ireq):
        return ireq
    else:
        return repository.find_best_match(ireq, prereleases=prereleases)


def update_ireq_name(install_requirement, package_name):
    # type: (pip.req.InstallRequirement, str) -> pip.req.InstallRequirement
    """Updates the name of an existing install requirement.

    Args:
        install_requirement: A :class:`pip.req.InstallRequirement`
            instance.
        package_name: The new package name.

    Returns:
        The **install_requirement** with mutated requirement name.

    """
    requirement = install_requirement.req
    if hasattr(requirement, 'project_name'):
        requirement.project_name = package_name
    else:
        requirement.name = package_name
    return install_requirement


def write_requirements(filename,               # type: str
                       requirements,           # type: IRequirementIter
                       index_url=None,         # type: Optional[str]
                       extra_index_urls=None,  # type: Optional[Iterable[str]]
                       header=None,            # type: Optional[str]
                       ):
    # type: (...) -> None
    """Writes install requirements to a file.

    Note that this function is destructive and will overwrite any
    existing files.

    Args:
        filename: The output filename.
        requirements: An iterable of :class:`pip.req.InstallRequirement`.
        index_url: The primary Python package index URL.
        extra_index_urls: Extra package index URLs.
        header: A header string to prepend to the file.

    """
    with atomicwrites.atomic_write(filename, overwrite=True) as f:
        if header:
            f.write(header)

        for ireq in sorted(requirements, key=lambda ireq: str(ireq)):
            f.write(piptools.utils.format_requirement(ireq))
            f.write('\n')
