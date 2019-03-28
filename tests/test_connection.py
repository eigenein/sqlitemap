from pytest import raises

from sqlitemap import Connection


def test_connection_len(connection: Connection):
    assert len(connection) == 0
    connection.get('collection')
    assert len(connection) == 1
    connection.get('collection')
    assert len(connection) == 1


def test_connection_iter(connection: Connection):
    assert list(connection) == []
    connection.get('collection')
    assert list(connection) == ['collection']


def test_connection_delitem(connection: Connection):
    connection.get('collection')
    del connection['collection']
    assert not list(connection)


def test_connection_getitem_value_error(connection: Connection):
    with raises(ValueError):
        connection.get('); drop tables --')


def test_connection_delitem_value_error(connection: Connection):
    with raises(ValueError):
        del connection['); drop tables --']


def test_connection_delitem_missing(connection: Connection):
    with raises(KeyError):
        del connection['missing']
