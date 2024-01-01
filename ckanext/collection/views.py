from __future__ import annotations

from flask import Blueprint

import ckan.plugins.toolkit as tk
from ckanext.collection import shared
from ckan.logic import parse_params

bp = Blueprint("ckanext-collection", __name__)


@bp.route("/api/util/collection/<name>/render")
def render(name: str) -> str | bytes:
    try:
        tk.check_access("collection_view_render", {}, {"name": name})
    except tk.NotAuthorized:
        return tk.abort(403)

    params = parse_params(tk.request.args)

    collection = shared.get_collection(name, params)

    if not collection:
        return tk.abort(404)

    return collection.serializer.render()
