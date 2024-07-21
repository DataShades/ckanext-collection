# Serializer

## Overview

Serializer converts data into textual, binary or any other alternative
representation. For example, if you want to transform records produced by the
`data` service of the collection into MessagePack, you should probably use
serializer.

Serializers are main users of columns service, because it contains details
about specific data columns. And serializers often iterate data service
directly(ignoring `range` method), to serialize all available records.

The only required method for serializer is `serialize`. This method must return
an data from `data` service transformed into format provided by serializer. For
example, `JsonSerializer` returns string with JSON-encoded data.

You are not restricted by textual or binary formats. Serializer that transforms
data into pandas' DataFrame is completely valid version of the serializer.

/// admonition
    type: example

```python
from array import array

class ArraySerializer(serialize.Serializer):
    def serialize(self):
        result = array("i")
        for item in self.attached.data:
            result.append(item)

        return result

col = collection.StaticCollection(
    serializer_factory=ArraySerializer,
    data_settings={"data": [1, 2, 3]}
)
assert col.serializer.serialize() == array("i", [1,2,3])
```
///

## Available serializer factories

::: collection.shared.serialize.Serializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.serialize.DictListSerializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.serialize.CsvSerializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.serialize.JsonlSerializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.serialize.JsonSerializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.serialize.HtmlSerializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        show_bases: false
        heading_level: 3
        members: []

::: collection.shared.serialize.TableSerializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        heading_level: 3
        members: []

::: collection.shared.serialize.HtmxTableSerializer
    options:
        show_root_heading: true
        show_root_toc_entry: true
        heading_level: 3
        members: []
