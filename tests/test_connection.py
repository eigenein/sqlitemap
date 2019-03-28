from sqlite3 import ProgrammingError

from pytest import raises

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


def test_delitem(connection: Connection):
    connection.get('collection')
    del connection['collection']
    assert not list(connection)


def test_getitem_value_error(connection: Connection):
    with raises(ValueError):
        connection.get('); drop tables --')


def test_delitem_value_error(connection: Connection):
    with raises(ValueError):
        del connection['); drop tables --']


def test_delitem_missing(connection: Connection):
    with raises(KeyError):
        del connection['missing']


def test_connection_setitem(connection: Connection):
    with raises(TypeError):
        connection['foo'] = ...


def test_close(connection: Connection):
    connection.close()
    with raises(ProgrammingError):
        _ = connection['foo']
