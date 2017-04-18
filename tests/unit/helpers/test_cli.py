# -*- coding: utf-8 -*-
from __future__ import absolute_import

import sh
import builtins
import sys

import six

import reqwire.helpers.cli


log_methods = (
    'echo',
    'error',
    'fatal',
    'info',
    'warn',
    'warning',
)


def test_emojize_win32(mocker):
    mocker.patch('sys.platform', 'win32')
    assert reqwire.helpers.cli.emojize(
        ':thumbs_up_sign: foo').encode('utf-8') == b'foo'


def test_emojize_linux(mocker):
    mocker.patch('sys.platform', 'linux')
    mocker.patch('io.open', mocker.mock_open(
        read_data='Linux version 4.4.0-31-generic (gcc version 5.3.1)'))
    assert reqwire.helpers.cli.emojize(
        ':thumbs_up_sign:').encode('utf-8') == b'\xf0\x9f\x91\x8d'


def test_emojize_linux_ioerror(mocker):
    mocker.patch('sys.platform', 'linux')
    io_open = mocker.patch('io.open', side_effect=IOError)
    assert reqwire.helpers.cli.emojize(
        ':thumbs_up_sign:').encode('utf-8') == b'\xf0\x9f\x91\x8d'


def test_emojize_wsl(mocker):
    mocker.patch('sys.platform', 'linux')
    mocker.patch('io.open', mocker.mock_open(
        read_data='Linux version 3.4.0-Microsoft (Microsoft@Microsoft.com)'))
    assert reqwire.helpers.cli.emojize(
        ':thumbs_up_sign: foo').encode('utf-8')  == b'foo'


def test_console_writer_quiet(mocker):
    click_echo = mocker.patch('click.echo')
    console = reqwire.helpers.cli.ConsoleWriter(verbose=False)
    for method in log_methods:
        getattr(console, method)('test')
        click_echo.assert_not_called()


def test_console_writer_verbose(mocker):
    mocker.patch('sys.platform', 'linux')
    mocker.patch('io.open', mocker.mock_open(
        read_data='Linux version 4.4.0-31-generic (gcc version 5.3.1)'))
    click_echo = mocker.patch('click.echo')
    console = reqwire.helpers.cli.ConsoleWriter(verbose=True)
    for method in log_methods:
        getattr(console, method)('test')
        fmt = console.format_strings.get(method, '{msg}')
        message = reqwire.helpers.cli.emojize(fmt.format(msg='test'))
        click_echo.assert_called_once_with(message)
        click_echo.reset_mock()


def test_build_with_pip_compile_options(cli_runner, mocker):
    from reqwire.cli import main
    pip_compile = mocker.patch.object(sh, 'pip_compile')
    result = cli_runner.invoke(main, ['build', '-t', 'main', '--', '--no-header'])
    assert result.exit_code == 0, result.output
    assert pip_compile.call_args[0][2] == '--no-header'


def test_main_remove(cli_runner):
    from reqwire.cli import main
    result = cli_runner.invoke(main, ['remove', 'Flask'])
    assert result.exit_code == 0, result.output
