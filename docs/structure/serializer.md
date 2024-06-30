# Serializer


Serializer converts data into textual, binary or any other alternative
representation. For example, if you want to compute records produced by the
`data` service of the collection into pandas' DataFrame, you should probably
use serializer.

Serializers are main users of columns service, because it contains details
about specific data columns. And serializers often iterate data service
directly(ignoring `range` method), to serialize all available records.

The only required method for serializer is `serialize`. This method must return
an data from `data` service transformed into format provided by serializer. For
example, `JsonSerializer` returns string with JSON-encoded data.

You are not restricted by textual or binary formats. Serializer that transforms
data into pandas' DataFrame is completely valid version of the serializer.

```python
class NewLineSerializer(Serializer):
    def serialize(self):
        result = ""
        for item in self.attached.data:
            result += str(item) + "\n"

        return result

col = StaticCollection(
    "name", {},
    serializer_factory=NewLineSerializer,
    data_settings={"data": [1, 2, 3]}
)
assert "".join(col.serializer.serialize()) == "1\n2\n3\n"
```
