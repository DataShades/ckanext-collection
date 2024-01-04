from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.logic import authz

from ckanext.collection import config


@tk.auth_allow_anonymous_access
def collection_view_render(context: types.Context, data_dict: dict[str, Any]):
    if data_dict["name"] in config.anonymous_collections():
        return {"success": True}

    if context["user"] and data_dict["name"] in config.authenticated_collections():
        return {"success": True}

    return {"success": False}


@tk.auth_allow_anonymous_access
def collection_view_export(context: types.Context, data_dict: dict[str, Any]):
    return authz.is_authorized("collection_view_render", context, data_dict)
