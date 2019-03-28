from typing import Iterable

from pytest import fixture

from sqlitemap import Connection


@fixture
def connection() -> Iterable[Connection]:
    with Connection(':memory:') as sqlite:
        yield sqlite
