import pytest

from ckanext.collection import shared


@pytest.fixture()
def collection_registry():
    """Collection registry cleaned after each test."""

    yield shared.collection_registry
    shared.collection_registry.reset()
