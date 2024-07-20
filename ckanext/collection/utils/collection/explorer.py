from __future__ import annotations

from typing import Any, Iterable

import ckan.plugins.toolkit as tk
from ckan.authz import is_authorized_boolean
from ckan.logic import parse_params

from ckanext.collection import internal, types
from ckanext.collection.utils.columns import TableColumns
from ckanext.collection.utils.data import Data
from ckanext.collection.utils.data.db import TableData
from ckanext.collection.utils.filters import DbFilters, Filters, TableFilters
from ckanext.collection.utils.serialize import HtmlSerializer, HtmxTableSerializer

from .base import Collection
from .db import DbCollection


class ExplorerSerializer(HtmlSerializer[types.TDataCollection]):
    extend_page_template: bool = internal.configurable_attribute(
        default_factory=lambda self: bool(
            tk.request and not tk.request.headers.get("hx-request"),
        ),
    )
    main_template: str = internal.configurable_attribute(
        "collection/serialize/explorer/main.html",
    )


class CollectionExplorer(Collection):
    """Collection of all registered collections.

    It exists for debugging and serves as an example of non-canonical usage of
    collections.
    """

    SerializerFactory = ExplorerSerializer.with_attributes(
        main_template="collection/serialize/collection_explorer/main.html",
    )

    class DataFactory(Data[Any, "CollectionExplorer"]):
        def compute_data(self) -> Iterable[Any]:
            params = parse_params(tk.request.args) if tk.request else {}
            names = self.attached.params.get("collection")
            if not names:
                return []

            if isinstance(names, str):
                names = [names]

            return [
                internal.get_collection(
                    name,
                    params,
                    serializer_settings={"extend_page_template": False},
                )
                for name in names
            ]

    class FiltersFactory(Filters["CollectionExplorer"], internal.UserTrait):
        static_collections: Iterable[str] = internal.configurable_attribute(
            default_factory=lambda self: list(
                map(str, internal.collection_registry.members),
            ),
        )

        def make_filters(self) -> Iterable[types.Filter[Any]]:
            return [
                types.SelectFilter(
                    name="collection",
                    type="select",
                    options={
                        "label": "Collection",
                        "options": [types.SelectOption(value="", text="")]
                        + [
                            types.SelectOption(value=name, text=name)
                            for name in self.static_collections
                            if name != self.attached.name
                            and is_authorized_boolean(
                                "collection_view_render",
                                {"user": self.user},
                                {"name": name},
                            )
                        ],
                    },
                ),
            ]


class DbExplorer(DbCollection):
    SerializerFactory = ExplorerSerializer.with_attributes(
        main_template="collection/serialize/db_explorer/main.html",
    )

    class DataFactory(Data[Any, "DbExplorer"]):
        def compute_data(self) -> Iterable[Any]:
            params = parse_params(tk.request.args)
            tables = self.attached.params.get("table")
            if not tables:
                return []

            if isinstance(tables, str):
                tables = [tables]

            _hidden = self.attached.params.get("hidden", "").split(",")
            hidden: set[str] = set(filter(None, map(str.strip, _hidden)))

            _visible = self.attached.params.get("visible", "").split(",")
            visible: set[str] = set(filter(None, map(str.strip, _visible))) - hidden

            _allowed_filters = self.attached.params.get("allowed_filters", "").split(
                ",",
            )
            allowed_filters: set[str] = set(
                filter(None, map(str.strip, _allowed_filters)),
            )

            _searchable_fields = self.attached.params.get(
                "searchable_fields",
                "",
            ).split(
                ",",
            )
            searchable_fields: set[str] = (
                set(filter(None, map(str.strip, _searchable_fields))) - allowed_filters
            )

            return [
                DbCollection(
                    name,
                    params,
                    db_connection_factory=self.attached.DbConnectionFactory,
                    data_factory=TableData.with_attributes(
                        table=name,
                        use_naive_filters=True,
                        use_naive_search=True,
                    ),
                    columns_factory=TableColumns.with_attributes(
                        table=name,
                        visible=visible or TableColumns.Default.NOT_HIDDEN,
                        hidden=hidden,
                        filterable=allowed_filters,
                        searchable=searchable_fields,
                    ),
                    filters_factory=TableFilters.with_attributes(table=name),
                    serializer_factory=HtmxTableSerializer,
                    serializer_settings={
                        "render_url": tk.h.url_for(
                            "ckanext-collection.render",
                            name=self.attached.name,
                            **{
                                k: v
                                for k, v in params.items()
                                if not k.startswith(f"{name}:")
                            },
                        ),
                    },
                )
                for name in tables
            ]

    class FiltersFactory(DbFilters["DbExplorer"]):
        static_tables: Iterable[str] = internal.configurable_attribute(
            default_factory=lambda self: [],
        )

        def make_filters(self) -> Iterable[types.Filter[Any]]:
            tables = self.static_tables
            if not tables:
                tables = self.attached.db_connection.inspector.get_table_names()

            return [
                types.SelectFilter(
                    name="table",
                    type="select",
                    options={
                        "label": "Table",
                        "options": [types.SelectOption(value="", text="")]
                        + [
                            types.SelectOption(value=name, text=name) for name in tables
                        ],
                    },
                ),
                types.InputFilter(
                    name="visible",
                    type="input",
                    options={
                        "label": "Visible columns(leave empty to show all columns)",
                        "placeholder": "comma-separated",
                    },
                ),
                types.InputFilter(
                    name="hidden",
                    type="input",
                    options={
                        "label": "Hidden columns",
                        "placeholder": "comma-separated",
                    },
                ),
                types.InputFilter(
                    name="allowed_filters",
                    type="input",
                    options={
                        "label": "Filterable columns(by exact values)",
                        "placeholder": "comma-separated",
                    },
                ),
                types.InputFilter(
                    name="searchable_fields",
                    type="input",
                    options={
                        "label": "Searchable columns(by case-insensitive fragment)",
                        "placeholder": "comma-separated",
                    },
                ),
            ]
