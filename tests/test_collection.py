from contextlib import suppress

from pytest import raises

from sqlitemap import Collection


def test_len(collection: Collection):
    assert len(collection) == 0
    collection['foo'] = 'bar'
    assert len(collection) == 1


def test_iter(collection: Collection):
    assert list(collection) == []
    collection['foo'] = 'bar'
    assert list(collection) == ['foo']


def test_values(collection: Collection):
    assert collection.values() == []
    collection['foo'] = 'bar'
    assert collection.values() == ['bar']


def test_getitem_by_key(collection: Collection):
    with raises(KeyError):
        _ = collection['foo']
    collection['foo'] = 'bar'
    assert collection['foo'] == 'bar'
    collection['foo'] = 'qux'
    assert collection['foo'] == 'qux'


def test_getitem_by_slice(collection: Collection):
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


def test_setitem(collection: Collection):
    collection['foo'] = 1
    assert collection['foo'] == 1


def test_delitem_by_key(collection: Collection):
    with raises(KeyError):
        del collection['foo']
    collection['foo'] = 42
    del collection['foo']
    with raises(KeyError):
        del collection['foo']


def test_delitem_by_slice(collection: Collection):
    collection['bar'] = 1
    collection['foo'] = 2
    collection['quw'] = 3
    collection['qux'] = 4
    collection['quy'] = 5
    collection['quz'] = 6
    del collection['bar':'quz':'qu%']
    assert list(collection) == ['bar', 'foo', 'quz']


def test_context_manager(collection: Collection):
    with collection:
        collection['foo'] = 42

    with suppress(KeyError), collection:
        collection['foo'] = 43
        del collection['bar']

    assert collection['foo'] == 42


def test_commit(collection: Collection):
    collection['foo'] = 42
    collection.commit()


def test_rollback(collection: Collection):
    collection['foo'] = 42
    collection.commit()
    collection['foo'] = 43
    assert collection['foo'] == 43
    collection.rollback()
    assert collection['foo'] == 42
