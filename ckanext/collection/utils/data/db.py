from __future__ import annotations

import abc
from typing import Any, Iterable

import sqlalchemy as sa
from sqlalchemy.sql.selectable import GenerativeSelect, Select

from ckanext.collection import internal, types

from .model import BaseSaData

# from pandas.compat._optional import import_optional_dependency
# import_optional_dependency("sqlalchemy", errors="ignore")


class DbData(BaseSaData[Select, types.TData, types.TDbCollection], abc.ABC):
    def _execute(self, stmt: GenerativeSelect):
        return self.attached.db_connection.engine.execute(stmt)


class TableData(DbData[types.TData, types.TDbCollection]):
    table: str = internal.configurable_attribute()
    static_columns: Iterable[Any] = internal.configurable_attribute(
        default_factory=lambda self: [],
    )

    def get_base_statement(self):
        columns = self.static_columns or [
            sa.column(c["name"])
            for c in self.attached.db_connection.inspector.get_columns(self.table)
        ]
        return sa.select(*columns).select_from(
            sa.table(self.table),
        )
