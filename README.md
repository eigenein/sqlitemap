# `sqlitemap`

Dictionary interface to an SQLite database.

[![Build Status](https://travis-ci.com/eigenein/sqlitemap.svg?branch=master)](https://travis-ci.com/eigenein/sqlitemap)
[![Coverage Status](https://coveralls.io/repos/github/eigenein/sqlitemap/badge.svg?branch=master)](https://coveralls.io/github/eigenein/sqlitemap?branch=master)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/sqlitemap.svg)](https://pypi.org/project/sqlitemap/)
[![PyPI – Version](https://img.shields.io/pypi/v/sqlitemap.svg)](https://pypi.org/project/sqlitemap/#history)
[![PyPI – Python](https://img.shields.io/pypi/pyversions/sqlitemap.svg)](https://pypi.org/project/sqlitemap/#files)
[![License](https://img.shields.io/pypi/l/sqlitemap.svg)](https://github.com/eigenein/sqlitemap/blob/master/LICENSE)

## Intro

…One day I needed an embedded key-value store for a pet project, but didn't find a «good enough» implementation. So, I made my own one.

It's a lightweight wrapper over the standard [sqlite3](https://docs.python.org/3/library/sqlite3.html) module. It provides the standard [`MutableMapping`](https://docs.python.org/3/library/typing.html#typing.MutableMapping) interface for an SQLite connection and SQLite table.

## `Connection`

You create an instance of `Connection` as if it was a normal [`sqlite3.connect`](https://docs.python.org/3/library/sqlite3.html#sqlite3.connect) call:

```python
from sqlitemap import Connection

connection = Connection(':memory:')
```

It implements the context manager interface, so you use `with` to make a transaction as if it was an `sqlite3.Connection`. And it implements `MutableMapping[str, Collection]`, except for `__setitem__`. So you can imagine a `Connection` as a dictionary of collections altogether with their names and do virtually everything you could do with a normal `dict`:

```python
from sqlitemap import Collection

# Collection is automatically created:
foo: Collection = connection['foo']

# You can iterate over collection names:
names = list(connection)

# Or even over collections:
collections = connection.values()

# Drop collection:
del connection['foo']

# Get number of collections:
len(connection)

# Special one, to close the connection:
connection.close()
```

Internally, collection is a table with two columns: `key: str` and `value: bytes`. So, you need some serialization to represent objects as byte strings. By default, `sqlitemap` uses the standard [`json`](https://docs.python.org/3/library/json.html) module. It picks up [`ujson`](https://pypi.org/project/ujson/) or [`orjson`](https://pypi.org/project/orjson/), if available. These are also available as `sqlitemap` extras: `sqlitemap[ujson]` and `sqlitemap[orjson]`.

Otherwise, you can specify any custom `Callable[[Any], bytes]` for encoder and `Callable[[bytes], Any]` for decoder:

```python
connection = Connection(':memory:', dumps_=custom_dumps, loads_=custom_loads)
``` 

TODO

## `Collection`

TODO
