from __future__ import annotations

from ckanext.collection.utils.data import StaticData

from .api import ApiCollection, ApiSearchCollection
from .base import Collection
from .db import DbCollection
from .explorer import CollectionExplorer, DbExplorer
from .model import ModelCollection

__all__ = [
    "Collection",
    "DbCollection",
    "ApiCollection",
    "ApiSearchCollection",
    "ModelCollection",
    "CollectionExplorer",
    "DbExplorer",
    "StaticCollection",
]


class StaticCollection(Collection):
    DataFactory = StaticData
