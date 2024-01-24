from __future__ import annotations

from werkzeug.utils import import_string

import ckan.plugins.toolkit as tk

from ckanext.collection import types


def anonymous_collections() -> list[str]:
    return tk.config["ckanext.collection.auth.anonymous_collections"]


def authenticated_collections() -> list[str]:
    return tk.config["ckanext.collection.auth.authenticated_collections"]


def include_htmx_asset() -> bool:
    return tk.config["ckanext.collection.include_htmx_asset"]


def htmx_init_modules() -> bool:
    return tk.config["ckanext.collection.htmx_init_modules"]


def serializer(format: str) -> type[types.BaseSerializer] | None:
    value = tk.config.get(f"ckanext.collection.export.{format}.serializer")
    if value:
        return import_string(value, silent=True)
    return None
