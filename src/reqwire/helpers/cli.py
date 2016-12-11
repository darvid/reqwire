"""Helpers for command-line applications."""
from __future__ import absolute_import

import io
import re
import sys

import click
import emoji


MYPY = False
if MYPY:  # pragma: no cover
    from typing import Any, Iterator, Tuple  # noqa: F401


__all__ = (
    'ConsoleWriter',
    'emojize',
)


def emojize(message, **kwargs):
    # type: (str, Any) -> str
    """Wrapper around :func:`emoji.emojize` for Windows compatibility.

    Emoji are not well supported under Windows. This function not only
    checks :data:`sys.platform`, but the file ``/proc/version`` as well
    to prevent *"emojification"* on the Windows Subsystem for Linux
    (WSL, otherwise known as Ubuntu on Windows).

    Args:
        message: The format string. See :func:`emoji.emojize` for more
            information. Any emoji placeholders will be removed if
            Windows or WSL are detected.
        **kwargs: Passed to :func:`emoji.emojize`.

    """
    emoji_pattern = r':(.+?):'
    if sys.platform == 'win32':
        return re.sub(emoji_pattern, '', message).strip()
    elif sys.platform.startswith('linux'):
        try:
            with io.open('/proc/version') as f:
                if 'Microsoft' in f.read():
                    return re.sub(emoji_pattern, '', message).strip()
        except IOError:
            pass
    return emoji.emojize(message, **kwargs)


class ConsoleWriter(object):
    """Facilitates writing formatted, informational messages to a TTY."""

    format_strings = {
        'error': click.style(':skull: {msg}', fg='red'),
        'fatal': click.style(':skull: {msg}', fg='red'),
        'warn': click.style(':warning: {msg}', fg='yellow'),
        'warning': click.style(':warning: {msg}', fg='yellow'),
    }

    def __init__(self, verbose=True):
        # type: (bool) -> None
        """Constructs a new :class:`ConsoleWriter`.

        Args:
            verbose: Sets verbosity for all future messages.

        """
        self.verbose = verbose

    def echo(self, message, *args, **kwargs):
        # type: (str, Any, Any) -> None
        """Wraps :func:`click.echo`.

        Args:
            message: The message to write to stdout.
            *args: Used to format message.
            **kwargs: Used to format message.

        """
        if self.verbose:
            click.echo(emojize(message.format(*args, **kwargs)))

    def error(self, message, *args, **kwargs):
        # type: (str, Any, Any) -> None
        """Prints an error message.

        Args:
            message: The message to write to stdout.
            *args: Used to format message.
            **kwargs: Used to format message.

        """
        self._echo_formatted('error', message, *args, **kwargs)

    def fatal(self, message, *args, **kwargs):
        # type: (str, Any, Any) -> None
        """Prints a fatal message.

        Args:
            message: The message to write to stdout.
            *args: Used to format message.
            **kwargs: Used to format message.

        """
        self._echo_formatted('fatal', message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        # type: (str, Any, Any) -> None
        """Prints an informational message.

        Args:
            message: The message to write to stdout.
            *args: Used to format message.
            **kwargs: Used to format message.

        """
        self._echo_formatted('info', message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        # type: (str, Any, Any) -> None
        """Prints a warning message.

        Args:
            message: The message to write to stdout.
            *args: Used to format message.
            **kwargs: Used to format message.

        """
        self._echo_formatted('warn', message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        # type: (str, Any, Any) -> None
        """Prints a warning message.

        Args:
            message: The message to write to stdout.
            *args: Used to format message.
            **kwargs: Used to format message.

        """
        self._echo_formatted('warn', message, *args, **kwargs)

    def _echo_formatted(self, format_key, message, *args, **kwargs):
        # type: (str, str, Any, Any) -> None
        fmt = self.format_strings.get(format_key, '{msg}')
        self.echo(fmt.format(msg=message), *args, **kwargs)
