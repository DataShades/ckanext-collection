from __future__ import annotations

from . import config

def collection_include_htmx_asset() -> bool:
    return config.include_htmx_asset()
