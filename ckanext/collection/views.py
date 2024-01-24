from __future__ import annotations

from flask import Blueprint

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.common import streaming_response
from ckan.logic import parse_params
from werkzeug.utils import secure_filename

from ckanext.collection import config, shared

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


@bp.route("/api/util/collection/<name>/export")
@bp.route("/api/util/collection/<name>/export/<format>")
def export(name: str, format: str | None = None) -> types.Response:
    try:
        tk.check_access("collection_view_export", {}, {"name": name})
    except tk.NotAuthorized:
        return tk.abort(403)

    params = parse_params(tk.request.args)

    collection = shared.get_collection(name, params)
    if not collection:
        return tk.abort(404)

    if format:
        serializer_factory = config.serializer(format)
        if not serializer_factory:
            return tk.abort(404)
        serializer = serializer_factory(collection)
        filename = f"collection.{format}"

    else:
        serializer = collection.serializer
        filename = "collection"

    filename = secure_filename(tk.request.args.get("filename", filename))

    resp = streaming_response(serializer.stream(), with_context=True)
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp
