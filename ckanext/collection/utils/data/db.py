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
        return sa.select(sa.text("*")).select_from(sa.table(self.table))
