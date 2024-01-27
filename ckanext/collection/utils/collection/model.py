from __future__ import annotations

from ckanext.collection import types
from ckanext.collection.utils.data import ModelData

from .base import Collection


class ModelCollection(Collection[types.TData]):
    DataFactory = ModelData
