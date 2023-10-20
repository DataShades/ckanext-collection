from __future__ import annotations
import abc
from typing import Generic

from ckanext.collection.types import TDataCollection


class AttachTrait(abc.ABC, Generic[TDataCollection]):
    _collection: TDataCollection

    def attach(self, obj: TDataCollection):
        self._collection = obj
