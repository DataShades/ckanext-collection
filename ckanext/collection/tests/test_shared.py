from __future__ import annotations

from typing import Any

import pytest
from faker import Faker

import ckan.plugins.toolkit as tk

from ckanext.collection import shared


class AttachExample(shared.AttachTrait[Any]):
    pass


@pytest.mark.parametrize(
    "obj",
    [(None,), (1,), (object(),), ("hello",), (AttachExample(),)],
)
def test_attached_object(obj: Any):
    """Anything can be attached as a collection to AttachTrait implementation."""
    example = AttachExample()
    example._attach(obj)
    assert example.attached is obj


class TestAttrSettings:
    def test_default_factories(self, faker: Faker):
        """Default factories are used when value is missing from settings."""
        name = "test"
        value = faker.pyint()
        another_value = faker.word()

        class Test(shared.AttrSettingsTrait):
            test = shared.configurable_attribute(default_factory=lambda self: value)

        obj = Test()

        obj._gather_settings({})
        assert getattr(obj, name) == value

        obj._gather_settings({name: another_value})
        assert getattr(obj, name) == another_value

    def test_without_factories(self, faker: Faker):
        """If defult factory is not specified, attribute is not created when
        it's missing from settings.

        """
        name = "test"
        value = faker.pyint()

        class Test(shared.AttrSettingsTrait):
            test = shared.configurable_attribute(None)

        obj = Test()

        obj._gather_settings({})
        assert getattr(obj, name) is None

        obj._gather_settings({name: value})
        assert getattr(obj, name) == value

    def test_declaration(self, faker: Faker):
        first = "first"
        second = "second"

        class Test(shared.AttrSettingsTrait):
            first = shared.configurable_attribute(default_factory=lambda self: "first")

        obj = Test()
        obj._gather_settings({})

        assert getattr(obj, first) == "first"

        class ChildTest(Test):
            first = shared.configurable_attribute(
                default_factory=lambda self: "new first",
            )

        obj = ChildTest()
        obj._gather_settings({})

        assert getattr(obj, first) == "new first"

        class AnotherChildTest(Test):
            second = shared.configurable_attribute(
                default_factory=lambda self: "second",
            )

        obj = AnotherChildTest()
        obj._gather_settings({})

        assert getattr(obj, first) == "first"
        assert getattr(obj, second) == "second"


@pytest.mark.usefixtures("clean_db")
def test_user_trait(user_factory: Any, faker: Faker, app_with_session: Any):
    fake_username = faker.name()

    class Test(shared.UserTrait):
        pass

    obj = Test()
    obj._gather_settings({})
    assert not obj.user

    with app_with_session.flask_app.test_request_context():
        user = user_factory.model()
        tk.login_user(user)

        obj._gather_settings({})
        assert obj.user == user.name

    obj._gather_settings({"user": fake_username})
    assert obj.user == fake_username