# Usage

Collection can be initialized anywhere in code

/// admonition
    type: example

```python
from my.module import MyCollection

col = Collection("", {})

```
///

But it's recommended to register collections globally.

Collections are registered via [ICollection interface](interfaces.md#icollection) or
via CKAN signals. Registered collection can be initialized anywhere in code
using helper and can be used in a number of generic endpoints that render
collection as HTML of export it into different formats.

/// tab | Register via interface
hello
///

/// tab | Register via signal
world
///

Registration via interface:

```python
from ckanext.collection.interfaces import CollectionFactory, ICollection


class MyPlugin(p.SingletonPlugin):
    p.implements(ICollection, inherit=True)

    def get_collection_factories(self) -> dict[str, CollectionFactory]:
        return {
            "my-collection": MyCollection,
        }

```

`get_collection_factories` returns a dictionary with collection names(letters,
digits, underscores and hyphens are allowed) as keys, and collection factories
as values. In most generic case, collection factory is just a collection
class. But you can use any function with signature `(str, dict[str, Any],
**Any) -> Collection` as a factory. For example, the following function is a
valid collection factory and it can be returned from `get_collection_factories`

```python
def my_factory(name: str, params: dict[str, Any], **kwargs: Any):
    """Collection that shows 100 numbers per page"""
    params.setdefault("rows_per_page", 100)
    return MyCollection(name, params, **kwargs)
```

If you want to register a collection only if collection plugin is enabled, you
can use CKAN signals instead of wrapping import from ckanext-collection into
try except block:

```python

class MyPlugin(p.SingletonPlugin):
    p.implements(p.ISignal)

    def get_signal_subscriptions(self) -> types.SignalMapping:
        return {
            tk.signals.ckanext.signal("collection:register_collections"): [
                self.collect_collection_factories,
            ],
        }

    def collect_collection_factories(self, sender: None):
        return {
            "my-collection": MyCollection,
        }

```

Data returned from the signal subscription is exactly the same as from
`ICollection.get_collection_factories`. The only difference, signal
subscription accepts `sender` argument which is always `None`, due to internal
implementation of signals.
