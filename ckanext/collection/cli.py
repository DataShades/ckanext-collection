from __future__ import annotations

import click

from ckanext.collection import shared

__all__ = ["collection"]


@click.group(short_help="ckanext-collection CLI")
def collection():
    pass


@collection.command("list")
@click.option("--name-only", is_flag=True, help="Show only collection names")
def list_collections(name_only: bool):
    """List all registered collections."""
    for name, collection in shared.collection_registry.members.items():
        line = name if name_only else f"{name}: {collection}"
        click.secho(line)
