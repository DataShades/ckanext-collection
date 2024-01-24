from __future__ import annotations

from . import config


def collection_include_htmx_asset() -> bool:
    """Check if HTMX needs to be added to webassets."""
    return config.include_htmx_asset()


def collection_init_modules_in_htmx_response():
    """Check if HTMX needs to be initialize CKAN modules for every HTMX response."""
    return config.htmx_init_modules()
