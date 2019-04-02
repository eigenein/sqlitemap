from sqlite3 import ProgrammingError

from pytest import mark, raises
from tests.constants import bad_table_names, good_table_names

from sqlitemap import Connection


def test_len(connection: Connection):
    assert len(connection) == 0
    connection.get('collection')
    assert len(connection) == 1
    connection.get('collection')
    assert len(connection) == 1


def test_iter(connection: Connection):
    assert list(connection) == []
    connection.get('collection')
    assert list(connection) == ['collection']


@mark.parametrize('name', good_table_names)
def test_delitem(connection: Connection, name: str):
    connection.get(name)
    del connection[name]
    assert not list(connection)


@mark.parametrize('name', good_table_names)
def test_getitem(connection: Connection, name: str):
    connection.get(name)


def test_getitem_cache(connection: Connection):
    assert connection['foo'] is connection['foo']
    assert connection['foo'] is not connection['bar']


@mark.parametrize('name', bad_table_names)
def test_getitem_value_error(connection: Connection, name: str):
    with raises(ValueError):
        connection.get(name)


@mark.parametrize('name', bad_table_names)
def test_delitem_value_error(connection: Connection, name: str):
    with raises(ValueError):
        del connection[name]


def test_delitem_missing(connection: Connection):
    with raises(KeyError):
        del connection['missing']


def test_delitem_cache(connection: Connection):
    collection = connection['foo']
    del connection['foo']
    assert connection['foo'] is not collection


def test_connection_setitem(connection: Connection):
    with raises(TypeError):
        connection['foo'] = ...


def test_close(connection: Connection):
    connection.close()
    with raises(ProgrammingError):
        _ = connection['foo']
