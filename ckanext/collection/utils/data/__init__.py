from __future__ import annotations

import logging
from typing import Iterable

from ckanext.collection import shared, types

from .api import ApiData, ApiListData, ApiSearchData
from .base import Data
from .db import DbData, TableData
from .model import BaseSaData, ModelData, StatementSaData, UnionSaData
from .stream import CsvData

__all__ = [
    "Data",
    "CsvData",
    "TableData",
    "ApiData",
    "ApiListData",
    "ApiSearchData",
    "UnionSaData",
    "UnionModelData",
    "StatementSaData",
    "StatementModelData",
    "BaseSaData",
    "BaseModelData",
    "DbData",
    "ModelData",
]

BaseModelData = BaseSaData
UnionModelData = UnionSaData
StatementModelData = StatementSaData

log = logging.getLogger(__name__)


class StaticData(Data[types.TData, types.TDataCollection]):
    """Static data source.

    This class turns existing iterable into a data source.
    """

    data: Iterable[types.TData] = shared.configurable_attribute(
        default_factory=lambda self: [],
    )

    def compute_data(self) -> Iterable[types.TData]:
        return self.data
