"""Provides configuration and configuration defaults."""
from __future__ import absolute_import

import pathlib

import biome


__all__ = (
    'env',
    'lockfile',
)

env = biome.reqwire
lockfile = env.get_path('lockfile', pathlib.Path('.reqwire.lock'))
