from typing import Any, Callable

from pytest import mark

from sqlitemap.json import (
    dumps,
    loads,
    orjson_dumps,
    orjson_loads,
    stdlib_dumps,
    stdlib_loads,
    ujson_dumps,
    ujson_loads,
)


@mark.parametrize('dumps_, loads_', [
    (orjson_dumps, orjson_loads),
    (stdlib_dumps, stdlib_loads),
    (ujson_dumps, ujson_loads),
])
@mark.parametrize('value, bytes_', [
    (None, b'null'),
])
def test_json(
    dumps_: Callable[[Any], bytes],
    loads_: Callable[[bytes], Any],
    value: Any,
    bytes_: bytes,
):
    assert dumps_(value) == bytes_
    assert loads_(bytes_) == value


def test_defaults():
    assert dumps is orjson_dumps
    assert loads is orjson_loads
