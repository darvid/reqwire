"""Provides the command-line entrypoint for reqwire."""
from __future__ import absolute_import

import pathlib
import tempfile

import atomicwrites
import click
import piptools.exceptions
import piptools.utils
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
              envvar='REQWIRE_DIR_BASE',
              help='Requirements directory.')
@click.option('-q', '--quiet/--verbose', default=False,
              help='Suppress output.')
@click.option('--extension', default='.in',
              help='File extension used for requirement source files. '
                   'Defaults to ".in".')
@click.option('--source-directory', default='src', envvar='REQWIRE_DIR_SOURCE',
              help='Source directory relative to requirements directory. '
                   'Defaults to "src".')
@click.option('--build-directory', default='lck', envvar='REQWIRE_DIR_BUILD',
              help='Build directory relative to requirements directory. '
                   'Defaults to "lck".')
@click.version_option(version=reqwire.__version__)
@click.pass_context
def main(ctx,
         directory,         # type: click.Context
         quiet,             # type: bool
         extension,         # type: str
         source_directory,  # type: str
         build_directory,   # type: str
         ):
    # type: (...) -> None
    """reqwire: micromanages your requirements."""
    requirements_dir = pathlib.Path(directory)
    console.verbose = not quiet
    ctx.obj = {
        'build_dir': build_directory,
        'directory': requirements_dir,
        'extension': extension,
        'source_dir': source_directory,
    }


@main.command('add')
@click.option('-b', '--build', default=False, is_flag=True,
              help='Builds the given tag(s) after adding packages.')
@click.option('-t', '--tag',
              help=('Target requirement tags. '
                    'Multiple tags supported. '
                    'Defaults to "main".'),
              multiple=True)
@click.option('--install/--no-install', default=True,
              help='Installs packages with pip.')
@click.option('--pin/--no-pin', default=True,
              help='Saves specifiers with pinned package versions.')
@click.option('--pre', default=False, is_flag=True,
              help='Include prerelease versions.')
@click.option('--resolve-canonical-names/--no-resolve-canonical-names',
              default=True,
              help='Queries Python package index for canonical package names.')
@click.option('--resolve-versions/--no-resolve-versions',
              default=True,
              help='Resolves and pins the latest package version.')
@click.argument('specifiers', nargs=-1)
@click.pass_obj
@click.pass_context
def main_add(ctx,                      # type: click.Context
             options,                  # type: Dict[str, Any]
             build,                    # type: bool
             tag,                      # type: Iterable[str]
             install,                  # type: bool
             pin,                      # type: bool
             pre,                      # type: bool
             resolve_canonical_names,  # type: bool
             resolve_versions,         # type: bool
             specifiers,               # type: Tuple[str, ...]
             ):
    # type: (...) -> None
    """Add packages to requirement source files."""
    if not options['directory'].exists():
        console.error('run `{} init\' first', ctx.find_root().info_name)
        ctx.abort()

    if install:
        if pre:
            specifiers = tuple(['--pre'] + list(specifiers))
        pip_install(ctx, *specifiers)

    if not tag:
        tag = ('main',)

    pip_options, session = reqwire.helpers.requirements.build_pip_session()
    src_dir = options['directory'] / options['source_dir']
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
                prereleases=pre,
                resolve_canonical_names=resolve_canonical_names,
                resolve_versions=resolve_versions)
    except piptools.exceptions.NoCandidateFound as err:
        console.error(str(err))
        ctx.abort()

    if build:
        ctx.invoke(main_build, all=False, tag=tag)


@main.command('build')
@click.option('-a', '--all', is_flag=True,
              help='Builds all tags.')
@click.option('-t', '--tag', help='Saves tagged requirement source files.',
              multiple=True)
@click.argument('pip_compile_options', nargs=-1)
@click.pass_obj
@click.pass_context
def main_build(ctx,                  # type: click.Context
               options,              # type: Dict[str, Any]
               all,                  # type: bool
               tag,                  # type: Iterable[str]
               pip_compile_options,  # type: Iterable[str]
               ):
    # type: (...) -> None
    """Build requirements with pip-compile."""
    if not options['directory'].exists():
        console.error('run `{} init\' first', ctx.find_root().info_name)
        ctx.abort()
    if not all and not tag:
        console.error('either --all or --tag must be provided.')
        ctx.abort()
    src_dir = options['directory'] / options['source_dir']
    dest_dir = options['directory'] / options['build_dir']
    if not dest_dir.exists():
        dest_dir.mkdir()
    default_args = ['-r']
    if not tag:
        pattern = '*{}'.format(options['extension'])
        tag = (path.stem for path in src_dir.glob(pattern))
    for tag_name in tag:
        src = src_dir / ''.join((tag_name, options['extension']))
        dest = dest_dir / '{}.txt'.format(tag_name)
        console.info('building {}', click.format_filename(str(dest)))
        args = default_args[:]
        args += [str(src)]
        args += list(pip_compile_options)
        with atomicwrites.AtomicWriter(str(dest), 'w', True).open() as f:
            f.write(reqwire.scaffold.MODELINES_HEADER)
            with tempfile.NamedTemporaryFile() as temp_file:
                args += ['-o', temp_file.name]
                sh.pip_compile(*args, _out=f, _tty_out=False)


@main.command('init')
@click.option('-f', '--force', help='Force initialization.', is_flag=True)
@click.option('-i', '--index-url', envvar='PIP_INDEX_URL',
              help='Base URL of Python package index.')
@click.option('-t', '--tag',
              help=('Tagged requirements files to create. '
                    'Defaults to docs, main, qa, and test.'),
              multiple=True)
@click.option('--extra-index-url', envvar='PIP_EXTRA_INDEX_URL',
              help='Extra URLs of package indexes',
              multiple=True)
@click.pass_obj
@click.pass_context
def main_init(ctx,              # type: click.Context
              options,          # type: Dict[str, Any]
              force,            # type: bool
              index_url,        # type: str
              tag,              # type: Iterable[str]
              extra_index_url,  # type: Tuple[str]
              ):
    # type: (...) -> None
    """Initialize reqwire in the current directory."""
    if not force and options['directory'].exists():
        console.error('requirements directory already exists')
        ctx.abort()
    src_dir = reqwire.scaffold.init_source_dir(
        options['directory'], exist_ok=force, name=options['source_dir'])
    console.info('created {}', click.format_filename(str(src_dir)))

    build_dir = reqwire.scaffold.init_source_dir(
        options['directory'], exist_ok=force, name=options['build_dir'])
    console.info('created {}', click.format_filename(str(build_dir)))

    if not tag:
        tag = ('docs', 'main', 'qa', 'test')
    for tag_name in tag:
        filename = reqwire.scaffold.init_source_file(
            working_directory=options['directory'],
            tag_name=tag_name,
            extension=options['extension'],
            index_url=index_url,
            extra_index_urls=extra_index_url)
        console.info('created {}', click.format_filename(filename))


@main.command('remove')
@click.option('-t', '--tag',
              help=('Tagged requirements files to create. '
                    'Defaults to docs, main, qa, and test.'),
              multiple=True)
@click.argument('specifiers', nargs=-1)
@click.pass_obj
@click.pass_context
def main_remove(ctx,
                options,
                tag,
                specifiers,
                ):
    # type: (...) -> None
    """Remove packages from requirement source files."""
    if not options['directory'].exists():
        console.error('run `{} init\' first', ctx.find_root().info_name)
        ctx.abort()

    if not tag:
        tag = ('main',)

    for tag_name in tag:
        filename = reqwire.scaffold.build_filename(
            working_directory=options['directory'],
            tag_name=tag_name,
            extension=options['extension'])
        if not filename.exists():
            console.warn('"{}" does not exist',
                         click.format_filename(str(filename)))
            continue
        req_file = reqwire.helpers.requirements.RequirementFile(
            str(filename))
        for specifier in specifiers:
            hireq = (reqwire.helpers.requirements.HashableInstallRequirement
                     .from_line(specifier))
            for requirement in req_file.requirements:
                src_req_name = piptools.utils.name_from_req(requirement)
                target_req_name = piptools.utils.name_from_req(hireq)
                if src_req_name == target_req_name:
                    req_file.requirements.remove(requirement)
                    console.info('removed "{}" from {}',
                                 src_req_name, tag_name)

        reqwire.helpers.requirements.write_requirements(
            filename=str(filename),
            requirements=req_file.requirements,
            header=reqwire.scaffold.build_source_header(
                index_url=req_file.index_url,
                extra_index_urls=req_file.extra_index_urls,
                nested_cfiles=req_file.nested_cfiles,
                nested_rfiles=req_file.nested_rfiles))
