"""Provides custom exception classes."""
from __future__ import absolute_import


__all__ = (
    'IndexUrlMismatchError',
    'ReqwireError',
)


class ReqwireError(Exception):
    """Base class for all exceptions thrown by reqwire."""


class IndexUrlMismatchError(ReqwireError):
    """Indicates a conflict between CLI and requirement source file."""
