from __future__ import annotations
import ckan.plugins.toolkit as tk


def anonymous_collections() -> list[str]:
    return tk.config["ckanext.collection.auth.anonymous_collections"]


def authenticated_collections() -> list[str]:
    return tk.config["ckanext.collection.auth.authenticated_collections"]


def include_htmx_asset() -> bool:
    return tk.config["ckanext.collection.include_htmx_asset"]
