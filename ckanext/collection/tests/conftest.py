import pytest

from ckanext.collection import internal


@pytest.fixture()
def collection_registry():
    """Collection registry cleaned after each test."""
    yield internal.collection_registry
    internal.collection_registry.reset()
