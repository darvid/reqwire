"""Provides configuration and configuration defaults."""
from __future__ import absolute_import

import pathlib

import biome


__all__ = (
    'env',
    'lockfile',
    'preserve_toplevel',
)

env = biome.reqwire
lockfile = env.get_path('lockfile', pathlib.Path('.reqwire.lock'))
preserve_toplevel = env.get_bool('preserve_toplevel', default=False)
