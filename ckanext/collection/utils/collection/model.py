from __future__ import annotations

from ckanext.collection.utils.data import ModelData

from .base import Collection


class ModelCollection(Collection):
    DataFactory = ModelData
