from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.sql.selectable import GenerativeSelect, Select

from ckanext.collection import shared, types

from .model import BaseSaData


class TableData(BaseSaData[Select, types.TData, types.TDbCollection]):
    table: str = shared.configurable_attribute()

    def _execute(self, stmt: GenerativeSelect):
        return self.attached.db_connection.engine.execute(stmt)

    def get_base_statement(self):
        columns = self.attached.db_connection.inspector.get_columns(self.table)
        return sa.select(*[sa.column(c["name"]) for c in columns]).select_from(
            sa.table(self.table),
        )
