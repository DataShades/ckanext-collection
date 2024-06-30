# Data


This service produces the data for collection. Every data service must:

* be Iterable and iterate over all available records by default
* define `total` property, that reflects number of available records so that
  `len(list(data)) == data.total`
* define `range(start: Any, end: Any)` method that returns slice of the data

Base class for data services - `Data` - already contains a simple version of
this logic. You need to define only one method to make you custom
implementations: `compute_data()`. When data if accessed for the first time,
`compute_data` is called. Its result cached and used for iteration in
for-loops, slicing via `range` method and size measurement via `total`
property.


```python
class CustomData(Data):
    def compute_data(self) -> Any:
        return "abcdefghijklmnopqrstuvwxyz"

col = Collection("name", {}, data_factory=CustomData)
assert list(col) == ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
assert col.data.total == 26
assert col.data.range(-3, None) == "xyz"

```

If you need more complex data source, make sure you defined `__iter__`,
`total`, and `range`:

```python
class CustomData(Data):
    names = configurable_attribute(default_factory=["Anna", "Henry", "Mary"])

    @property
    def total(self):
        return len(self.names)

    def __iter__(self):
        yield from sorted(self.names)

    def range(self, start: Any, end: Any):
        if not isinstance(start, str) or not isinstance(end, str):
            return []

        for name in self:
            if name < start:
                continue
            if name > end:
                break
            yield name

```
