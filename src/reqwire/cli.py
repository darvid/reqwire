"""Provides the command-line entrypoint for reqwire."""
from __future__ import absolute_import

import pathlib

import click
import piptools.exceptions
import sh

import reqwire
import reqwire.helpers.cli
import reqwire.helpers.requirements
import reqwire.scaffold


MYPY = False
if MYPY:
    from typing import Any, Dict, Iterable, Set, Tuple  # noqa: F401


__all__ = ('main',)


console = reqwire.helpers.cli.ConsoleWriter()


def pip_install(ctx, *specifiers):
    # type: (click.Context, str) -> None
    try:
        result = sh.pip.install(*specifiers, _err_to_out=True, _iter=True)
        for line in result:
            click.echo(line, nl=False)
    except sh.ErrorReturnCode:
        ctx.abort()


@click.group()
@click.option('-d', '--directory', default='requirements',
              help='Requirements directory.')
@click.option('-q', '--quiet/--verbose', default=False,
              help='Suppress output.')
@click.option('--extension', default='.in',
              help=('File extension used for requirement source files. '
                    'Defaults to ".in".'))
@click.version_option(version=reqwire.__version__)
@click.pass_context
def main(ctx, directory, quiet, extension):
    # type: (click.Context, str, str, bool) -> None
    """reqwire: micromanages your requirements."""
    requirements_dir = pathlib.Path(directory)
    console.verbose = not quiet
    ctx.obj = {
        'directory': requirements_dir,
        'extension': extension,
    }


@main.command()
@click.option('-t', '--tag',
              help=('Target requirement tags. '
                    'Multiple tags supported. '
                    'Defaults to "main".'),
              multiple=True)
@click.option('--install/--no-install', default=True,
              help='Installs packages with pip.')
@click.option('--pin/--no-pin', default=True,
              help='Saves specifiers with pinned package versions.')
@click.option('--resolve-canonical-names/--no-resolve-canonical-names',
              default=True,
              help='Queries Python package index for canonical package names.')
@click.option('--resolve-versions/--no-resolve-versions',
              default=True,
              help='Resolves and pins the latest package version.')
@click.argument('specifiers', nargs=-1)
@click.pass_obj
@click.pass_context
def add(ctx,                      # type: click.Context
        options,                  # type: Dict[str, Any]
        tag,                      # type: Iterable[str]
        install,                  # type: bool
        pin,                      # type: bool
        resolve_canonical_names,  # type: bool
        resolve_versions,         # type: bool
        specifiers,               # type: Tuple[str]
        ):
    # type: (...) -> None
    """Add packages to requirement source files."""
    if install:
        pip_install(ctx, *specifiers)

    if not tag:
        tag = ('main',)

    pip_options, session = reqwire.helpers.requirements.build_pip_session()
    src_dir = options['directory'] / 'src'
    lookup_index_urls = set()  # type: Set[str]

    for tag_name in tag:
        filename = src_dir / ''.join((tag_name, options['extension']))
        if not filename.exists():
            continue
        _, finder = reqwire.helpers.requirements.parse_requirements(
            filename=str(filename))
        lookup_index_urls |= set(finder.index_urls)

    try:
        for tag_name in tag:
            console.info('saving requirement(s) to {}', tag_name)
            reqwire.scaffold.extend_source_file(
                working_directory=options['directory'],
                tag_name=tag_name,
                specifiers=specifiers,
                extension=options['extension'],
                lookup_index_urls=lookup_index_urls,
                resolve_canonical_names=resolve_canonical_names,
                resolve_versions=resolve_versions)
    except piptools.exceptions.NoCandidateFound as err:
        console.error(str(err))
        ctx.abort()


@main.command()
@click.option('-a', '--all', is_flag=True,
              help='Builds all tags.')
@click.option('-t', '--tag', help='Saves tagged requirement source files.',
              multiple=True)
@click.argument('pip_compile_options', nargs=-1)
@click.pass_obj
@click.pass_context
def build(ctx,                  # type: click.Context
          options,              # type: Dict[str, Any]
          all,                  # type: bool
          tag,                  # type: Iterable[str]
          pip_compile_options,  # type: Iterable[str]
          ):
    # type: (...) -> None
    """Builds requirements with pip-compile."""
    if not all and not tag:
        console.error('either --all or --tag must be provided.')
        ctx.abort()
    src_dir = options['directory'] / 'src'
    dest_dir = options['directory'] / 'build'
    default_args = ['-r']
    if not tag:
        pattern = '*{}'.format(options['extension'])
        tag = (path.stem for path in src_dir.glob(pattern))
    for tag_name in tag:
        src = src_dir / ''.join((tag_name, options['extension']))
        dest = dest_dir / '{}.txt'.format(tag_name)
        console.info('building {}', click.format_filename(dest))
        args = default_args
        args += [str(src), '-o', str(dest)]
        args += list(pip_compile_options)
        sh.pip_compile(*args)


@main.command()
@click.option('-f', '--force', help='Force initialization.', is_flag=True)
@click.option('-i', '--index-url', envvar='PIP_INDEX_URL',
              help='Base URL of Python package index.')
@click.option('-t', '--tag',
              help=('Tagged requirements files to create. '
                    'Defaults to main, qa, and test.'),
              multiple=True)
@click.option('--extra-index-url', envvar='PIP_EXTRA_INDEX_URL',
              help='Extra URLs of package indexes',
              multiple=True)
@click.pass_obj
@click.pass_context
def init(ctx,              # type: click.Context
         options,          # type: Dict[str, Any]
         force,            # type: bool
         index_url,        # type: str
         tag,              # type: Iterable[str]
         extra_index_url,  # type: Tuple[str]
         ):
    # type: (...) -> None
    """Initialize reqwire in the current directory."""
    if not force and options['directory'].exists():
        console.error('requirements directory already exists', fg='red')
        ctx.abort()
    src_dir = reqwire.scaffold.init_source_dir(
        options['directory'], exist_ok=force)
    console.info('created {}', click.format_filename(src_dir))

    build_dir = reqwire.scaffold.init_source_dir(
        options['directory'], exist_ok=force, name='build')
    console.info('created {}', click.format_filename(build_dir))

    if not tag:
        tag = ('main', 'qa', 'test')
    for tag_name in tag:
        filename = reqwire.scaffold.init_source_file(
            working_directory=options['directory'],
            tag_name=tag_name,
            extension=options['extension'],
            index_url=index_url,
            extra_index_urls=extra_index_url)
        console.info('created {}', click.format_filename(filename))
