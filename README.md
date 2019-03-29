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

connection = Connection(':memory:', ...)
```

It implements the [context manager](https://docs.python.org/3/library/stdtypes.html#typecontextmanager) interface, so you use `with` to make a transaction as if it was an [`sqlite3.Connection`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection). And it implements `MutableMapping[str, Collection]`, except for `__setitem__`. So you can imagine a `Connection` as a dictionary of collections altogether with their [names](https://stackoverflow.com/questions/3694276/what-are-valid-table-names-in-sqlite) and do virtually everything you could do with a normal [`dict`](https://docs.python.org/3.7/library/stdtypes.html#dict):

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

## `Collection`

`Collection` also implements the [context manager](https://docs.python.org/3/library/stdtypes.html#typecontextmanager) interface to make a transaction, and `MutableMapping[str, Any]`:

### Setting an item

```python
with raises(KeyError):
    _ = collection['foo']
collection['foo'] = 'bar'
assert collection['foo'] == 'bar'
collection['foo'] = 'qux'
assert collection['foo'] == 'qux'
```

`key` column is a primary key.

### Retrieving keys

```python
assert list(collection) == []
collection['foo'] = 'bar'
assert list(collection) == ['foo']
```

### Retrieving values

```python
assert collection.values() == []
collection['foo'] = 'bar'
assert collection.values() == ['bar']
```

### Deleting an item

```python
with raises(KeyError):
    del collection['foo']
collection['foo'] = 42
del collection['foo']
with raises(KeyError):
    del collection['foo']
```

### Using slices

`Collection.__getitem__` and `Collection.__setitem__` also support [slices](https://docs.python.org/3/library/functions.html#slice) as their arguments. Slice `start` is then converted to `key >= start` clause, `stop` to `key < stop` and `step` to `key LIKE step`. All of these are combined with the `AND` operator. `Collection.__getitem__` also applies `ORDER BY key` clause, so it's possible to make some more sophisticated queries:

```python
collection['bar'] = 1
collection['foo'] = 2
collection['quw'] = 3
collection['qux'] = 4
collection['quy'] = 5
collection['quz'] = 6
assert collection['foo':] == [2, 3, 4, 5, 6]
assert collection[:'foo'] == [1]
assert collection[::'qu%'] == [3, 4, 5, 6]
assert collection['bar':'quz':'qu%'] == [3, 4, 5]
```

The same also works with `del collection [...]`. It deletes the rows that would be selected with the corresponding `__getitem__` call:

```python
collection['bar'] = 1
collection['foo'] = 2
collection['quw'] = 3
collection['qux'] = 4
collection['quy'] = 5
collection['quz'] = 6
del collection['bar':'quz':'qu%']
assert list(collection) == ['bar', 'foo', 'quz']
```

## Controlling transactions

`sqlitemap` does nothing special to control transactions. For that refer to [the standard library documentation](https://docs.python.org/3/library/sqlite3.html#controlling-transactions).
