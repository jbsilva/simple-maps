"""
Simple Maps - A Python client and CLI for the Cartes.io mapping platform.

This package provides both a programmatic API and command-line interface for interacting with
Cartes.io, a free and open-source mapping platform.

Example:
    >>> from simple_maps import Cartes, MapCreatePayload
    >>> api = Cartes()
    >>> maps = api.map_list()
    >>> new_map = api.map_create(MapCreatePayload(title="My Map"))

CLI Usage:
    $ simple_maps map list
    $ simple_maps map create --title "My Map"
    $ simple_maps marker create --map-id UUID --lat 40.7 --lng -74.0

"""

from .cartes import (
    Cartes,
    MapCreatePayload,
    MapListParams,
    MarkerCreatePayload,
    MarkerLocationPayload,
    Permission,
    Privacy,
)


__all__ = [
    "Cartes",
    "MapCreatePayload",
    "MapListParams",
    "MarkerCreatePayload",
    "MarkerLocationPayload",
    "Permission",
    "Privacy",
]
