from __future__ import annotations

from typing import Any

from typing_extensions import Self

from ckanext.collection import types
from ckanext.collection.utils.columns import TableColunns
from ckanext.collection.utils.data import TableData
from ckanext.collection.utils.db_connection import DbConnection

from .base import Collection


class DbCollection(Collection[types.TData], types.BaseDbCollection[types.TData]):
    _service_names: tuple[str, ...] = ("db_connection",) + Collection._service_names
    DbConnectionFactory: type[DbConnection[Self]] = DbConnection
    DataFactory = TableData
    ColumnsFactory = TableColunns

    def make_db_connection(self, **kwargs: Any) -> DbConnection[Self]:
        """Return connection."""
        return self.DbConnectionFactory(self, **kwargs)
