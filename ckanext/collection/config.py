from __future__ import annotations

from werkzeug.utils import import_string

import ckan.plugins.toolkit as tk

from ckanext.collection import types

CONFIG_ANNONYMOUS = "ckanext.collection.auth.anonymous_collections"
CONFIG_AUTHENTICATED = "ckanext.collection.auth.authenticated_collections"
CONFIG_INCLUDE_ASSET = "ckanext.collection.include_htmx_asset"
CONFIG_INIT_MODULES = "ckanext.collection.htmx_init_modules"


def anonymous_collections() -> list[str]:
    return tk.config[CONFIG_ANNONYMOUS]


def authenticated_collections() -> list[str]:
    return tk.config[CONFIG_AUTHENTICATED]


def include_htmx_asset() -> bool:
    return tk.config[CONFIG_INCLUDE_ASSET]


def htmx_init_modules() -> bool:
    return tk.config[CONFIG_INIT_MODULES]


def serializer(format: str) -> type[types.BaseSerializer] | None:
    value = tk.config.get(f"ckanext.collection.export.{format}.serializer")
    if value:
        return import_string(value, silent=True)
    return None
