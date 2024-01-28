from __future__ import annotations

from ckanext.collection import types
from ckanext.collection.utils.data import StaticData

from .api import ApiCollection, ApiListCollection, ApiSearchCollection
from .base import Collection
from .db import DbCollection
from .explorer import CollectionExplorer, DbExplorer
from .model import ModelCollection

__all__ = [
    "Collection",
    "DbCollection",
    "ApiCollection",
    "ApiSearchCollection",
    "ApiListCollection",
    "ModelCollection",
    "CollectionExplorer",
    "DbExplorer",
]


class StaticCollection(Collection[types.TData]):
    DataFactory = StaticData
