"""Helpers for managing Python package requirements."""
from __future__ import absolute_import

import enum
import io
import itertools
import optparse
import pathlib
import shlex
import typing

import atomicwrites
import ordered_set
import pip.basecommand
import pip.cmdoptions
import pip.download
import pip.exceptions
import pip.models
import pip.req
import pip.req.req_file
import piptools.repositories
import piptools.resolver
import piptools.utils
import requests
import six
import six.moves


MYPY = False
if MYPY:  # pragma: no cover
    from typing import Any, Iterable, Optional, Set, Tuple  # noqa: F401

    InstallReqIterable = Iterable['HashableInstallRequirement']
    InstallReqSet = Set['HashableInstallRequirement']
    InstallReqFileSet = Set['RequirementFile']

    ParseResultType = Tuple[
        InstallReqSet,
        Set[str],
        Set['RequirementFile'],
        Set['RequirementFile'],
    ]


__all__ = (
    'build_ireq_set',
    'get_canonical_name',
    'HashableInstallRequirement',
    'parse_requirements',
    'PyPiHtmlParser',
    'PyPiHtmlParserState',
    'RequirementFile',
    'resolve_ireqs',
    'resolve_specifier',
    'update_ireq_name',
    'write_requirements',
)


class _PipCommand(pip.basecommand.Command):

    name = '_PipCommand'


class HashableInstallRequirement(typing.Hashable, pip.req.InstallRequirement):
    """A hashable version of :class:`pip.req.InstallRequirement`."""

    @classmethod
    def from_ireq(cls, ireq):
        # type: (pip.req.InstallRequirement) -> HashableInstallRequirement
        """Builds a new instance from an existing install requirement."""
        return cls(
            req=ireq.req,
            comes_from=ireq.comes_from,
            source_dir=ireq.source_dir,
            editable=ireq.editable,
            link=ireq.link,
            as_egg=ireq.as_egg,
            update=ireq.update,
            pycompile=ireq.pycompile,
            markers=ireq.markers,
            isolated=ireq.isolated,
            options=ireq.options,
            wheel_cache=ireq._wheel_cache,
            constraint=ireq.constraint)

    def __eq__(self, other):  # noqa: D105
        # type: (Any) -> bool
        # TODO(dpg): Compare the underlying requirement only, rather
        # than the InstallRequirement
        return str(self) == str(other)

    def __hash__(self):  # noqa: D105
        # type: () -> int
        return hash(str(self))


class PyPiHtmlParser(six.moves.html_parser.HTMLParser, object):
    """An HTML parse for Python package indexes."""

    def __init__(self, search=None, *args, **kwargs):  # noqa: D102
        super(PyPiHtmlParser, self).__init__(*args, **kwargs)
        self.search = search.lower() if search is not None else None
        self.state = PyPiHtmlParserState.waiting
        self.collected_packages = []

    def handle_starttag(self, tag, attrs):  # noqa: D102
        if tag == 'a':
            self.state = PyPiHtmlParserState.collecting_package_name

    def handle_endtag(self, tag):  # noqa: D102
        if (tag == 'a' and
                self.state == PyPiHtmlParserState.collecting_package_name):
            self.state = PyPiHtmlParserState.waiting

    def handle_data(self, data):  # noqa: D102
        if self.state == PyPiHtmlParserState.collecting_package_name:
            self.collected_packages.append(data)
            if self.search is not None and data.lower() == self.search:
                self.state = PyPiHtmlParserState.found_package_name


class PyPiHtmlParserState(enum.IntEnum):
    """An enumeration of parsing states for :class:`PyPiHtmlParser`."""

    #: The default parser state.
    waiting = 0
    #: The state indicating a package anchor tag is being visited.
    collecting_package_name = 1
    #: The state indicating a package matching a search was visited.
    found_package_name = 2


class RequirementFile(object):
    """Represents a Python requirements.txt file."""

    def __init__(self,
                 filename,            # type: str
                 requirements=None,   # type: Optional[InstallReqSet]
                 nested_cfiles=None,  # type: Optional[InstallReqFileSet]
                 nested_rfiles=None,  # type: Optional[InstallReqFileSet]
                 index_urls=None,     # type: Optional[List[str]]
                 ):
        # type: (...) -> None
        """Constructs a new :class:`RequirementFile`.

        Args:
            filename: The path to a requirements file. The requirements
                file is not required to exist.
            requirements: A set of :class:`HashableInstallRequirement`.
                If **filename** points to a path that exists and
                **requirements** are not provided, then the requirements
                will be parsed from the target file.
            nested_cfiles: A set of :class:`RequirementFile`.
            nested_rfiles: A set of :class:`RequirementFile`.
            index_urls: A set of Python package index URLs. The first
                URL is assumed to be the primary index URL, while the
                rest are extra.

        """
        self.filename = pathlib.Path(filename)
        self.requirements = requirements or ordered_set.OrderedSet()
        self.index_urls = ordered_set.OrderedSet(index_urls)
        self.nested_cfiles = nested_cfiles or ordered_set.OrderedSet()
        self.nested_rfiles = nested_rfiles or ordered_set.OrderedSet()

        if requirements is None and self.filename.exists():
            self.reload()

    @property
    def index_url(self):
        # type: () -> Optional[str]
        """A Python package index URL."""
        if len(self.index_urls):
            return self.index_urls[0]

    @property
    def extra_index_urls(self):
        # type: () -> Set[str]
        """Extra Python package index URLs."""
        if len(self.index_urls) > 1:
            return self.index_urls[1:]
        return ordered_set.OrderedSet()

    def parse(self, *args):
        # type: (str) -> ParseResultType
        """Parses a requirements file.

        Args:
            *args: Command-line options and arguments passed to pip.

        Returns:
            A set of requirements, index URLs, nested constraint files,
            and nested requirements files.

            The nested constraint and requirements files are sets of
            :class:`RequirementFile` instances.

        """
        self.nested_files = self.parse_nested_files()
        pip_options, session = build_pip_session(*args)
        repository = piptools.repositories.PyPIRepository(pip_options, session)
        requirements = pip.req.parse_requirements(
            str(self.filename),
            finder=repository.finder,
            session=repository.session,
            options=pip_options)
        requirements = ordered_set.OrderedSet(sorted(
            (HashableInstallRequirement.from_ireq(ireq)
             for ireq in requirements),
            key=lambda ireq: str(ireq)))
        index_urls = ordered_set.OrderedSet(repository.finder.index_urls)
        nested_cfiles, nested_rfiles = self.parse_nested_files()
        nested_requirements = set(itertools.chain(
            *(requirements_file.requirements
              for requirements_file in nested_rfiles)))
        requirements -= nested_requirements
        return requirements, index_urls, nested_cfiles, nested_rfiles

    def parse_nested_files(self):
        # type: () -> Tuple[InstallReqFileSet, InstallReqFileSet]
        """Parses a requirements file, looking for nested files.

        Returns:
            A set of constraint files and requirements files.

        """
        nested_cfiles = ordered_set.OrderedSet()
        nested_rfiles = ordered_set.OrderedSet()
        parser = pip.req.req_file.build_parser()
        defaults = parser.get_default_values()
        defaults.index_url = None
        with io.open(str(self.filename), 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                args_str, options_str = pip.req.req_file.break_args_options(
                    line)
                opts, _ = parser.parse_args(shlex.split(options_str), defaults)
                if opts.requirements:
                    filename = self.filename.parent / opts.requirements[0]
                    nested_rfiles.add(self.__class__(str(filename)))
                elif opts.constraints:
                    filename = self.filename.parent / opts.constraints[0]
                    nested_cfiles.add(self.__class__(str(filename)))
        return nested_cfiles, nested_rfiles

    def reload(self):
        # type: () -> None
        """Reloads the current requirements file."""
        parsed_requirements = self.parse()
        self.requirements = parsed_requirements[0]
        self.index_urls = parsed_requirements[1]
        self.nested_cfiles = parsed_requirements[2]
        self.nested_rfiles = parsed_requirements[3]

    def __str__(self):  # noqa: D105
        # type: () -> str
        # TODO(dpg): serialize actual requirements.txt?
        return str(self.filename)

    def __repr__(self):  # noqa: D105
        # type: () -> str
        return '<{}(filename={!r})>'.format(
            self.__class__.__name__,
            str(self.filename))


def build_ireq_set(specifiers,                    # type: Iterable[str]
                   index_urls=None,  # type: Optional[Iterable[str]]
                   prereleases=False,             # type: bool
                   resolve_canonical_names=True,  # type: bool
                   resolve_versions=True,         # type: bool
                   sort_specifiers=True,          # type: bool
                   ):
    # type: (...) -> InstallReqSet
    """Builds a set of install requirements.

    Args:
        specifiers: A list of specifier strings.
        index_urls: List of Python package indexes. Only used if
            **resolve_canonical_names** or **resolve_versions** is
            ``True``.
        prereleases: Whether or not to include prereleases.
        resolve_canonical_names: Queries package indexes provided by
            **index_urls** for the canonical name of each
            specifier. For example, *flask* will get resolved to
            *Flask*.
        resolve_versions: Queries package indexes for latest package
            versions.
        sort_specifiers: Sorts specifiers alphabetically.

    Returns:
        A set of :class:`HashableInstallRequirement`.

    """
    install_requirements = ordered_set.OrderedSet()
    if sort_specifiers:
        specifiers = sorted(specifiers)
    for specifier in specifiers:
        if resolve_versions:
            args = []
            for index_url in index_urls:
                args.extend(['--extra-index-url', index_url])
            ireq = resolve_specifier(specifier, prereleases, *args)
        else:
            ireq = HashableInstallRequirement.from_line(specifier)
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

    Returns:
        The canonical name of a package, or ``None`` if no packaging
        could be found in the given search indexes.

    """
    if not index_urls:  # pragma: no cover
        index_urls = {pip.models.PyPI.simple_url}
    for index_url in index_urls:
        response = requests.get(index_url, stream=True)
        parser = PyPiHtmlParser(search=package_name)
        for line in response.iter_lines():
            parser.feed(six.text_type(line, response.encoding, 'ignore'))
            if parser.state == PyPiHtmlParserState.found_package_name:
                parser.close()
                return parser.collected_packages[-1]
        parser.close()
    raise pip.exceptions.DistributionNotFound(
        'No matching distribution found for {}'.format(package_name))


def parse_requirements(filename, *args):  # pragma: no cover
    # type: (str, str) -> Tuple[InstallReqSet, pip.index.PackageFinder]
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


def resolve_ireqs(requirements,       # type: InstallReqIterable
                  prereleases=False,  # type: bool
                  intersect=False,    # type: bool
                  *args,              # type: str
                  **kwargs            # type: Any
                  ):  # pragma: no cover
    # type: (...) -> InstallReqSet
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
                       requirements,           # type: InstallReqIterable
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
