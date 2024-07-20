"""Views of the extension."""

from __future__ import annotations

from flask import Blueprint
from werkzeug.utils import secure_filename

import ckan.plugins.toolkit as tk
from ckan import types
from ckan.common import streaming_response
from ckan.logic import parse_params

from ckanext.collection import config, shared
from ckanext.collection.utils.serialize import StreamingSerializer

bp = Blueprint("ckanext-collection", __name__)


try:
    from ckanext.ap_main.views.generics import ApConfigurationPageView

    class ApConfiguration(ApConfigurationPageView):
        """Config page for admin panel."""

    bp.add_url_rule(
        "/admin-panel/config/collection",
        view_func=ApConfiguration.as_view("ap_config", "ckanext-collection-ap-config"),
    )

except ImportError:
    pass


@bp.route("/api/util/collection/<name>/render")
def render(name: str) -> str | bytes:
    """Render public collection."""
    try:
        tk.check_access("collection_view_render", {}, {"name": name})
    except tk.NotAuthorized:
        return tk.abort(403)

    params = parse_params(tk.request.args)

    collection = shared.get_collection(name, params)

    if not collection:
        return tk.abort(404)

    return collection.serializer.serialize()


@bp.route("/api/util/collection/<name>/export")
@bp.route("/api/util/collection/<name>/export/<format>")
def export(name: str, format: str | None = None) -> types.Response:
    """Serialize and download public collection."""
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

    if not isinstance(serializer, StreamingSerializer):
        return tk.abort(409, "This collection does not support streaming export")

    filename = secure_filename(tk.request.args.get("filename", filename))

    resp = streaming_response(serializer.stream(), with_context=True)
    resp.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp
