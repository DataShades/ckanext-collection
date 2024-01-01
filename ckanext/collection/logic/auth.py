from __future__ import annotations
from typing import Any

from ckan import types
import ckan.plugins.toolkit as tk
from ckanext.collection import config


@tk.auth_allow_anonymous_access
def collection_view_render(context: types.Context, data_dict: dict[str, Any]):
    if data_dict["name"] in config.anonymous_collections():
        return {"success": True}

    if context["user"] and data_dict["name"] in config.authenticated_collections():
        return {"success": True}

    return {"success": False}
