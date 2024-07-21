# Data

## Overview

This service produces the data for collection. Every data service must:

* be `Iterable`
* yield all existing records during iteration. I.e, if data service produces
  datasets from `package_search` API, `list(data)` must contain **all**
  datasets from the search index, not only first 10 or 20.
* define `total` property, that reflects number of available records so that
  `len(list(data)) == data.total`
* define `range(start: Any, end: Any)` method that returns slice of the data

Base class for data services - `Data` - already contains a simple version of
this logic. Just override `compute_data()` and return a sequence with records
from it, to satisfy minimal requirements of the data service.


/// admonition
    type: example


```python
class MyData(data.Data):
    def compute_data(self):
        return "abcdefghijklmnopqrstuvwxyz"
```

```pycon
>>> col = collection.Collection(data_factory=MyData)
>>> list(col)
["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
>>> col.data.total
26
>>> col.data.range(-3, None)
"xyz"

```
///

Using `compute_data` simplifies defining data services, but it's not
required. You can explicitly implement all methods

/// admonition
    type: example

```pycol
class MyData(data.Data):
    letters = "abcdefghijklmnopqrstuvwxyz"

    @property
    def total(self):
        return len(self.letters)

    def __iter__(self):
        yield from self.letters

    def range(self, start, end):
        return self.letters[start:end]

```
///


## Base `Data` class

This class defines a couple of standard helpers in addition to minimal
requirements of data service

The most important, it caches result of `compute_data` when data or data length
is accessed. Because of it, items and length of the data service are not
updated in runtime.

/// admonition
    type: example

In the following example, items from data service and its length are not
changed after assigning to `items`, because of `compute_data` called only
during first access to data. After this point, data service uses cached result
of the first `compute_data` call.

```python
class MyData(data.Data):
    items = [1, 2, 3]

    def compute_data(self):
      return self.items
```
```pycon
>>> col = collection.Collection(data_factory=MyData)
>>> list(col.data)
[1, 2, 3]
>>> col.data.total
3
>>> col.data.items = [] # (1)!
>>> list(col.data)
[1, 2, 3]
>>> col.data.total
3
```

1. This has no sense, because data is already cached and `items` property will
   not be used anymore

To reset the cache and use `compute_data` again, call `refresh_data()` method
of the data service.

```pycon
>>> col.data.items = "hello"
>>> col.data.refresh_data()
>>> list(col.data)
["h", "e", "l", "l", "o"]
>>> col.data.total
5
```

///

Base `Data` class expects that `compute_data` returns a
[`collections.abc.Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence).
With this expectation it implements `range(start, end)` that returns slice of
the data, and `at(index)` that returns element with specified index.

/// admonition
    type: example

```python
class MyData(data.Data):
    def compute_data(self):
       return "hello world"
```

```pycon
>>> col = collection.Collection(data_factory=MyData)
>>> col.data.at(4)
"o"
>>> col.data.range(6, None)
"world"
```

These methods are also accessible via index operator.

```pycon
>>> col.data[4]
"o"
>>> col.data[6:]
"world"
```

///


If you are not going to rely on `compute_data` when extending `Data` class,
implement your own caching logic and index-acces, if you need them.

## Available data factories

These factories are available at `ckanext.collection.shared.data`.

::: collection.shared.data.Data
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.data.StaticData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.data.CsvFileData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.data.ApiData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.data.ApiSearchData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        heading_level: 3
        members: []

::: collection.shared.data.BaseSaData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.data.TemporalSaData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        heading_level: 3
        members: []

::: collection.shared.data.StatementSaData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        heading_level: 3
        members: []


::: collection.shared.data.UnionSaData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        heading_level: 3
        members: []

::: collection.shared.data.ModelData
    options:
        show_root_heading: true
        show_root_toc_entry: true
        heading_level: 3
        members: []
