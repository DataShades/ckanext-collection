from __future__ import annotations

import logging
from typing import Iterable

from ckanext.collection import internal, types

from .api import ApiData, ApiSearchData
from .base import Data
from .db import DbData, TableData
from .misc import CsvFileData
from .model import BaseSaData, ModelData, StatementSaData, UnionSaData

__all__ = [
    "Data",
    "CsvFileData",
    "TableData",
    "ApiData",
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

    This class produce items from its `data` attribute. Use any sequence as a
    value for `data` during initialization.

    Attributes:
        data: sequence of items produced by the service

    Example:
        ```python
        NumericData = data.StaticData.with_attributes(data=range(1, 20))

        UppercaseData = data.StaticData.with_attributes(
            data="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        )
        ```
        ```pycon
        >>> col = collection.Collection(data_factory=NumericData)
        >>> list(col)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        ```
    """

    data: Iterable[types.TData] = internal.configurable_attribute(
        default_factory=lambda self: [],
    )

    def compute_data(self) -> Iterable[types.TData]:
        return self.data
