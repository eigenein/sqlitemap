"""
Dictionary interface to an SQLite database.
"""

import re
import sqlite3
from abc import ABC
from contextlib import AbstractContextManager, closing
from os import PathLike
from typing import Any, Callable, Iterator, List, MutableMapping, Pattern, Tuple, TypeVar, Union, cast

from sqlitemap.json import dumps, loads

T = TypeVar('T')

table_name_re: Pattern = re.compile(r'[a-zA-Z\d_]+')


class ConnectionWrapper(AbstractContextManager, ABC):
    """
    Provides shared methods for the connection wrappers.
    """

    connection: sqlite3.Connection

    def __init__(self, dumps_: Callable[[Any], bytes], loads_: Callable[[bytes], Any]):
        self.dumps = dumps_
        self.loads = loads_

    def __enter__(self: T) -> T:
        """
        Enter a new transaction.
        """
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Leave the current transaction.
        """
        self.connection.__exit__(exc_type, exc_value, traceback)

    def commit(self):
        """
        Commit the current transaction.
        """
        self.connection.commit()

    def rollback(self):
        """
        Roll back the current transaction.
        """
        self.connection.rollback()


class Collection(ConnectionWrapper, MutableMapping[str, Any]):
    """
    Represents a collection.
    Provides the dictionary interface to an SQLite table.
    """

    def __init__(
        self,
        connection: sqlite3.Connection,
        name: str,
        dumps_: Callable[[Any], bytes],
        loads_: Callable[[bytes], Any],
    ):
        super().__init__(dumps_, loads_)
        self.connection = connection
        self.name = name
        with closing(connection.cursor()) as cursor:
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS `{name}` (
                    `key` TEXT NOT NULL PRIMARY KEY,
                    `value` BLOB NOT NULL
                )
            ''')

    def __len__(self) -> int:
        """
        Get size of the collection.
        """
        with closing(self.connection.execute(f'SELECT COUNT(1) FROM `{self.name}`')) as cursor:
            return cursor.fetchone()[0]

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over the collection keys.
        This is not really effective since it keeps the entire key set in memory.
        """
        with closing(self.connection.execute(f'SELECT `key` from `{self.name}`')) as cursor:
            return iter([key for key, in cursor])

    def values(self) -> List[Any]:
        """
        Get the collection values.
        This is not really effective since it keeps the entire value set in memory.
        """
        with closing(self.connection.execute(f'SELECT `value` from `{self.name}`')) as cursor:
            return [self.loads(value) for value, in cursor]

    def __getitem__(self, key: Union[str, slice]) -> Any:
        """
        Get the collection item or items.
        Supports addressing by both a single key or a slice.
        Returns list of values if a slice is provided.
        """
        # Slice flow.
        if isinstance(key, slice):
            query, parameters = self.make_slice_query(key)
            query = ['SELECT `value`', *query, 'ORDER BY `key`']
            with closing(self.connection.execute(' '.join(query), parameters)) as cursor:
                return [self.loads(value) for value, in cursor]

        # Single item flow.
        with closing(self.connection.execute(f'SELECT `value` FROM `{self.name}` WHERE `key` = ?', [key])) as cursor:
            row = cursor.fetchone()
            if row is None:
                raise KeyError(key)
            return self.loads(row[0])

    def __delitem__(self, key: Union[str, slice]) -> None:
        """
        Delete the item or items.
        Supports addressing by both a single key or a slice.
        """
        # Slice flow.
        if isinstance(key, slice):
            query, parameters = self.make_slice_query(key)
            query = ['DELETE', *query]
            with closing(self.connection.execute(' '.join(query), parameters)):
                return

        # Single item flow.
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(f'DELETE FROM `{self.name}` WHERE `key` = ?', [key])
            cursor.execute('SELECT changes()')
            if not cursor.fetchone()[0]:
                raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Set the collection item.
        """
        with closing(self.connection.cursor()) as cursor:
            cursor.execute(
                f'INSERT OR REPLACE INTO `{self.name}` (`key`, `value`) VALUES (?, ?)',
                [key, self.dumps(value)],
            )

    def make_slice_query(self, key: slice) -> Tuple[List[str], List[str]]:
        """
        Makes query clause for the slice-based operations.
        """
        query = [f'FROM `{self.name}` WHERE 1']
        parameters: List[str] = []
        if key.start is not None:
            query.append('AND `key` >= ?')
            parameters.append(cast(str, key.start))
        if key.stop is not None:
            query.append('AND `key` < ?')
            parameters.append(cast(str, key.stop))
        if key.step is not None:
            query.append('AND `key` LIKE ?')
            parameters.append(cast(str, key.step))
        return query, parameters


class Connection(ConnectionWrapper, MutableMapping[str, Collection]):
    """
    Represents a connection and wraps a standard SQLite connection.
    Provides the dictionary interface to collections.
    """

    def __init__(
        self,
        database: Union[str, bytes, PathLike],
        dumps_: Callable[[Any], bytes] = dumps,
        loads_: Callable[[bytes], Any] = loads,
        **kwargs: Any,
    ):
        super().__init__(dumps_, loads_)
        self.connection = sqlite3.connect(database, **kwargs)

    def __len__(self) -> int:
        with closing(self.connection.execute('''
            SELECT COUNT(*) FROM sqlite_master WHERE type = 'table'
        ''')) as cursor:
            return cursor.fetchone()[0]

    def __iter__(self) -> Iterator[str]:
        """
        Iterate over collection names.
        """
        with closing(self.connection.execute('''
            SELECT name FROM sqlite_master WHERE type = 'table'
        ''')) as cursor:
            for name, in cursor:
                yield name

    def __getitem__(self, name: str) -> Collection:
        """
        Get a collection by name.
        """
        if not table_name_re.match(name):
            raise ValueError(f'incorrect table name: {name}')
        return Collection(self.connection, name, self.dumps, self.loads)

    def __setitem__(self, name: str, value: Collection) -> None:
        raise TypeError('setting an entire collection is not supported')

    def __delitem__(self, name: str) -> None:
        """
        Drop the collection.
        """
        if not table_name_re.match(name):
            raise ValueError(f'incorrect table name: {name}')
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute(f'DROP TABLE `{name}`')
        except sqlite3.OperationalError as e:
            raise KeyError(name) from e

    def close(self):
        """
        Close the current connection.
        """
        self.connection.close()
