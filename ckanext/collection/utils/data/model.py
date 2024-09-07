from __future__ import annotations

import abc
import logging
from datetime import date
from functools import cached_property
from typing import Any, Generic, Iterable, Iterator, TypeVar, cast

import sqlalchemy as sa
from sqlalchemy.orm import Mapper
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.elements import Label
from sqlalchemy.sql.selectable import GenerativeSelect, Select

from ckan import model
from ckan.types import AlchemySession

from ckanext.collection import internal, types

from .base import Data

log = logging.getLogger(__name__)
TStatement = TypeVar("TStatement", bound=GenerativeSelect)


class BaseSaData(
    Data[types.TData, types.TDataCollection],
    Generic[TStatement, types.TData, types.TDataCollection],
):
    """Abstract data source for SQL statements.

    This class can be extended to build data source over SQL statement. Its
    `compute_data` calls 4 methods:

    * `get_base_statement`: produces initial statement
    * `alter_statement(stmt)`: modifies statement or replaces it completely
    * `statement_with_filters(stmt)`: apply `WHERE` and `HAVING` conditions
    * `statement_with_sorting(stmt)`: apply `ORDER BY`

    These methods do nothing by default, but can be replaced in sublcasses to
    build SQL statement gradually.

    Warning:
        Final statement produced by `compute_data` and total number of results
        are cached. Call `refresh_data()` method of the service to rebuild the
        statement and refresh number of rows.

    Attributes:
        use_naive_filters: search by filterable columns from `params`. Default: true
        use_naive_search: if `params` contains `q`, ILIKE it against searchable
            columns. Default: true
        session: SQLAlchemy session
        is_scalar: return only first column from each row

    Example:
        ```python
        import sqlalchemy as sa
        from ckan import model

        class UserData(data.BaseSaData):
            def get_base_statement(self):
                return sa.select(model.User.name)
        ```

        ```pycon
        >>> col = collection.Collection(data_factory=UserData)
        >>> list(col)
        [("default",), (...,)]
        ```

    """

    _data: cached_property[TStatement]
    is_scalar: bool = internal.configurable_attribute(False)

    use_naive_filters: bool = internal.configurable_attribute(True)
    use_naive_search: bool = internal.configurable_attribute(True)
    session: AlchemySession = internal.configurable_attribute(
        default_factory=lambda self: model.Session,
    )

    EMPTY_STRING = object()

    def compute_data(self):
        stmt = self.get_base_statement()
        stmt = self.alter_statement(stmt)
        stmt = self.statement_with_filters(stmt)
        return self.statement_with_sorting(stmt)

    @abc.abstractmethod
    def get_base_statement(self) -> Any:
        """Return statement with minimal amount of columns and filters."""
        ...

    def compute_total(self, data: TStatement) -> int:
        return self.count_statement(data)

    def __iter__(self) -> Iterator[types.TData]:
        yield from self.execute_statement(self._data)

    def _execute(self, stmt: GenerativeSelect):
        return self.session.execute(stmt)

    def range(self, start: int, end: int) -> Iterable[types.TData]:
        stmt = self._data.limit(end - start).offset(start)
        return self.execute_statement(stmt)

    def execute_statement(self, stmt: TStatement) -> Iterable[types.TData]:
        result: Any
        if self.is_scalar:
            result = self.session.scalars(stmt)

        else:
            result = self.session.execute(stmt)

        return result

    def alter_statement(self, stmt: TStatement):
        """Add columns, joins and unconditional filters to statement."""
        return stmt

    def count_statement(self, stmt: TStatement) -> int:
        """Count number of items in query."""
        count_stmt: Select = sa.select(sa.func.count()).select_from(stmt)
        return cast(int, self._execute(count_stmt).scalar())

    def _into_clause(self, column: ColumnElement[Any], value: Any):
        if isinstance(value, list):
            return column.in_(value)

        if value is self.EMPTY_STRING:
            value = ""

        column_type = column.type.python_type
        if not isinstance(value, column_type) and value is not None:
            value = str(value)  # noqa: PLW2901
            column = sa.func.cast(column, sa.Text)

        return column == value

    def statement_with_filters(self, stmt: TStatement) -> TStatement:
        """Add normal filter to statement."""
        if not isinstance(stmt, Select):
            return stmt

        params = self.attached.params
        if self.use_naive_filters:
            filters = [
                name
                for name in self.attached.columns.filterable
                if name in params
                and params[name] != ""
                and name in stmt.selected_columns
            ]

            if filters:
                stmt = stmt.where(
                    sa.and_(
                        *[
                            self._into_clause(stmt.selected_columns[name], params[name])
                            for name in filters
                        ],
                    ),
                )

        if self.use_naive_search:
            if (q := params.get("q")) and "q" not in self.attached.columns.searchable:
                filters = [
                    name
                    for name in self.attached.columns.searchable
                    if name in stmt.selected_columns
                ]
                if filters:
                    stmt = stmt.where(
                        sa.or_(
                            *[
                                stmt.selected_columns[name].ilike(f"%{q}%")
                                for name in filters
                            ],
                        ),
                    )
            for name in self.attached.columns.searchable:
                if name not in params or name not in stmt.selected_columns:
                    continue
                value = params[name]
                stmt = stmt.where(stmt.selected_columns[name].ilike(f"%{value}%"))

        return stmt

    def statement_with_sorting(self, stmt: TStatement):
        """Specify sorting order for statement."""
        sort = self.attached.params.get("sort")
        if not sort:
            return stmt

        column, desc = internal.parse_sort(sort)

        if column not in self.attached.columns.sortable:
            log.warning("Unexpected sort value: %s", column)
            return stmt

        if column not in stmt.selected_columns:
            sort = column
            if desc:
                sort = f"{sort} DESC"
            return stmt.order_by(sa.text(sort))

        col_object = stmt.selected_columns[column]

        return stmt.order_by(col_object.desc() if desc else col_object.asc())


class TemporalSaData(BaseSaData[TStatement, types.TData, types.TDataCollection]):
    """Data source that supports pagination by datetime column.

    Attributes:
        temporal_column: column used for pagination

    Example:
        This class can be used as a base for SQL statement based data
        services. Collection that uses such data service must also use
        `pager.TemporalPager` instead of the default `pager.ClassicPager`.

        ```python
        import sqlalchemy as sa
        from datetime import date, timedelta
        from ckan import model

        class TemporalPackageData(data.TemporalSaData):
            def get_base_statement(self):
                return sa.select(model.Package.name, model.Package.metadata_created)
        ```

        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=TemporalPackageData,
        >>>     data_settings={"temporal_column": model.Package.metadata_created},
        >>>     pager_factory=pager.TemporalPager,
        >>>     pager_settings={"since": datetime.now() - timedelta(days=40)},
        >>> )
        >>> list(col)
        [("pkg1", datetime.datetime(2024, 6, 13, 10, 40, 22, 518511)), ...]
        ```

    """

    temporal_column: ColumnElement[Any] = internal.configurable_attribute()

    def range(self, start: date | None, end: date | None) -> Iterable[types.TData]:  # type: ignore
        stmt = self._data
        if not isinstance(stmt, Select):
            return self.execute_statement(stmt)

        if isinstance(self.temporal_column, str):
            col = stmt.selected_columns[self.temporal_column]
        else:
            col = self.temporal_column

        if start:
            stmt = stmt.where(col >= start)
        if end:
            stmt = stmt.where(col < end)

        return self.execute_statement(stmt)


class StatementSaData(BaseSaData[Select, types.TData, types.TDataCollection]):
    """Data source for arbitrary SQL statement.

    Warning:
        Final statement produced by `compute_data` and total number of results
        are cached. Call `refresh_data()` method of the service to rebuild the
        statement and refresh number of rows.

    Attributes:
        statement (sqlalchemy.sql.Select): select statement

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.StatementSaData,
        >>>     data_settings={"statement": sa.select(model.User.name)},
        >>> )
        >>> list(col)
        [("default",), (...,)]
        ```

    """

    statement: Any = internal.configurable_attribute(None)

    def get_base_statement(self):
        """Return statement with minimal amount of columns and filters."""
        return self.statement


class UnionSaData(BaseSaData[Select, types.TData, types.TDataCollection]):
    """Data source for multiple SQL statement merged with UNION ALL.

    Warning:
        Final statement produced by `compute_data` and total number of results
        are cached. Call `refresh_data()` method of the service to rebuild the
        statement and refresh number of rows.

    Attributes:
        statements (sqlalchemy.sql.Select): select statements

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.UnionSaData,
        >>>     data_settings={"statements": [
        >>>         sa.select(model.User.name, sa.literal("user")),
        >>>         sa.select(model.Package.name, sa.literal("package")),
        >>>         sa.select(model.Group.name, sa.literal("group")),
        >>>     ]},
        >>> )
        >>> list(col)
        [("default", "user"),
        ("warandpeace", "package"),
        ("my-cool-group", "group")]
        ```
    """

    statements: Iterable[GenerativeSelect] = internal.configurable_attribute(
        default_factory=lambda self: [],
    )

    def get_base_statement(self):
        """Return statement with minimal amount of columns and filters."""
        return sa.select(sa.union_all(*self.statements).subquery())


class ModelData(BaseSaData[Select, types.TData, types.TDataCollection]):
    """Data source for SQLAlchemy model.

    Warning:
        Final statement produced by `compute_data` and total number of results
        are cached. Call `refresh_data()` method of the service to rebuild the
        statement and refresh number of rows.

    Attributes:
        model: main model used by data source
        is_scalar: return model instance instead of collection of columns.
            /// details
                type: example

            Non-scalar collection returns rows as tuples of columns
            ```pycon
            >>> col = collection.Collection(
            >>>     data_factory=data.ModelData,
            >>>     data_settings={
            >>>         "model": model.User,
            >>>         "is_scalar": False,
            >>>     },
            >>> )
            >>> list(col)
            [("id-123-123", "user-name", ...), ...]
            ```

            Scalar collection yields model instances
            ```pycon
            >>> col = collection.Collection(
            >>>     data_factory=data.ModelData,
            >>>     data_settings={
            >>>         "model": model.User,
            >>>         "is_scalar": True,
            >>>     },
            >>> )
            >>> list(col)
            [<User id=id-123-123 name=user-name>, ...]
            ```
            ///
        static_columns: select only specified columns. If `is_scalar` flag
            enabled, only first columns from this list is returned.
            /// details
                type: example

            Non-scalar collection with `static_columns` produces tuples with values
            ```pycon
            >>> col = collection.Collection(
            >>>     data_factory=data.ModelData,
            >>>     data_settings={
            >>>         "model": model.User,
            >>>         "is_scalar": False,
            >>>         "static_columns": [model.User.name, model.User.sysadmin],
            >>>     },
            >>> )
            >>> list(col)
            [("default", True), ...]
            ```

            Scalar collection with `static_columns` yields values of the first column
            ```pycon
            >>> col = collection.Collection(
            >>>     data_factory=data.ModelData,
            >>>     data_settings={
            >>>         "model": model.User,
            >>>         "is_scalar": True,
            >>>         "static_columns": [model.User.name, model.User.sysadmin],
            >>>     },
            >>> )
            >>> list(col)
            ["default", ...]
            ```
            ///

        static_filters: apply filters to the select statement
            /// details
                type: example

            Filters are values produced by operations with model columns. The
            same thing you'd pass into `.filter`/`.where` methods.

            ```pycon
            >>> col = collection.Collection(
            >>>     data_factory=data.ModelData,
            >>>     data_settings={
            >>>         "model": model.User,
            >>>         "is_scalar": True,
            >>>         "static_filters": [model.User.sysadmin == True],
            >>>     },
            >>> )
            >>> list(col)
            [<User sysadmin=True ...>, ...]
            ```
            ///

    Example:
        ```pycon
        >>> col = collection.Collection(
        >>>     data_factory=data.ModelData,
        >>>     data_settings={"model": model.User, "is_scalar": True},
        >>> )
        >>> list(col)
        [<User ...>, ...]
        ```

    """

    model: Any = internal.configurable_attribute(None)
    static_columns: list[sa.Column[Any] | Label[Any]] = internal.configurable_attribute(
        default_factory=lambda self: [],
    )
    static_filters: list[Any] = internal.configurable_attribute(
        default_factory=lambda self: [],
    )
    static_sources: dict[str, Any] = internal.configurable_attribute(
        default_factory=lambda self: {},
    )
    static_joins: list[tuple[str, Any, bool]] = internal.configurable_attribute(
        default_factory=lambda self: [],
    )

    def select_columns(self) -> Iterable[Any]:
        """Return list of columns for select statement."""
        if self.static_columns:
            return self.static_columns

        if not self.model:
            return []

        mapper = cast(Mapper, sa.inspect(self.model))
        return [self.model] if self.is_scalar else [mapper.columns]

    def get_extra_sources(self) -> dict[str, Any]:
        """Return mapping of additional models/subqueries for statement.

        Note: Don't call this method direclty. Instead, use `extra_sources`
        property, that caches return value of the current method. Extra sources
        must not change during query building process.

        Extra sources are used when the query contains subqueries or joins with
        aliased models. For example, in order to select column from joined
        subquery, instead of creating identical subqueries inside
        `select_columns` and `get_joins`, write the following code:

        >>> def get_extra_sources(self):
        >>>     return {"subq": make_subquery()}
        >>>
        >>> def select_columns(self):
        >>>     return [self.extra_sources["subq"].c.column_name]
        >>>
        >>> def get_joins(self):
        >>>     subq = self.extra_sources["subq"]
        >>>     return [("subq", subq.c.id == self.model.id, False)]

        """
        return self.static_sources

    @cached_property
    def extra_sources(self) -> dict[str, Any]:
        """Cache for extra sources.

        If you are going to override this property, don't forget to add
        `cached_property` decorator. The better option would be to override
        `get_extra_sources`. In this way you will not be affected if cache
        implementation changes in future.
        """
        return self.get_extra_sources()

    def get_joins(self) -> Iterable[tuple[str, Any, bool]]:
        """Return join details for extra_sources.

        Every item is a tuple of of (extra_source_name, join_condition,
        outerjoin_flag)
        """
        return self.static_joins

    def apply_joins(self, stmt: Select) -> Select:
        """Return list of columns for select statement."""
        sources = self.extra_sources

        for name, condition, isouter in self.get_joins():
            stmt = stmt.join(sources[name], condition, isouter=isouter)

        return stmt

    def get_base_statement(self):
        """Return statement with minimal amount of columns and filters."""
        columns = self.select_columns()
        stmt = sa.select(*columns)
        if self.model:
            stmt = stmt.select_from(self.model)

        return self.apply_joins(stmt)

    def statement_with_filters(self, stmt: Select):
        """Add normal filter to statement."""
        for cond in self.static_filters:
            stmt = stmt.where(cond)

        return super().statement_with_filters(stmt)
