"""
Automatically detects the best way to serialize values to JSON.
"""

import json
from typing import Any, Callable


def stdlib_loads(value: bytes) -> Any:
    return json.loads(value.decode())


def stdlib_dumps(value: Any) -> bytes:
    return json.dumps(value).encode()


loads = stdlib_loads
dumps = stdlib_dumps

try:
    import ujson
except ImportError:
    pass
else:
    def ujson_loads(value: bytes) -> Any:
        return ujson.loads(value.decode())

    def ujson_dumps(value: Any) -> bytes:
        return ujson.dumps(value).encode()

    loads = ujson_loads
    dumps = ujson_dumps

try:
    import orjson
except ImportError:
    pass
else:
    orjson_loads: Callable[[bytes], Any] = orjson.loads
    orjson_dumps: Callable[[Any], bytes] = orjson.dumps

    loads = orjson_loads
    dumps = orjson_dumps
