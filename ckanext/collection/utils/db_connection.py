from __future__ import annotations

from typing import Any, cast

import sqlalchemy as sa
from sqlalchemy.engine import Engine

from ckan import model

from ckanext.datastore.backend.postgres import get_read_engine

from ckanext.collection import internal, types


class DbConnection(types.BaseDbConnection, internal.Domain[types.TDbCollection]):
    engine: Engine = internal.configurable_attribute()

    @property
    def inspector(self):
        return sa.inspect(self.engine)


class UrlDbConnection(DbConnection[types.TDbCollection]):
    url: str = internal.configurable_attribute()
    engine_options: dict[str, Any] = internal.configurable_attribute(
        default_factory=lambda self: {},
    )

    def __init__(self, obj: types.TDbCollection, /, **kwargs: Any):
        super().__init__(obj, engine=None, **kwargs)
        self.engine = sa.create_engine(self.url, **self.engine_options)


class CkanDbConnection(DbConnection[types.TDbCollection]):
    engine: Engine = internal.configurable_attribute(
        default_factory=lambda self: cast(Engine, model.meta.engine),
    )


class DatastoreDbConnection(DbConnection[types.TDbCollection]):
    engine: Engine = internal.configurable_attribute(
        default_factory=lambda self: get_read_engine(),
    )
