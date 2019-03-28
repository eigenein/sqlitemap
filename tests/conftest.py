from pytest import fixture

from sqlitemap import Collection, Connection


@fixture
def connection() -> Connection:
    return Connection(':memory:')


@fixture
def collection(connection: Connection) -> Collection:
    return connection['test']
