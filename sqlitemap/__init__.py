from __future__ import annotations

import re
import sqlite3
from abc import ABC
from contextlib import AbstractContextManager, closing
from os import PathLike
from typing import Any, Iterator, MutableMapping, Pattern, Union

table_name_re: Pattern = re.compile(r'[a-zA-Z\d_]+')


class ConnectionWrapper(ABC):
    """
    Provides shared methods for the connection wrappers.
    """

    connection: sqlite3.Connection

    def commit(self):
        """
        Commit current transaction.
        """
        self.connection.commit()

    def rollback(self):
        """
        Rollback current transaction.
        """
        self.connection.rollback()


class Collection(ConnectionWrapper, AbstractContextManager, MutableMapping[str, Any]):
    """
    Represents a collection.
    Provides the dictionary interface to an SQLite table.
    """

    def __init__(self, connection: sqlite3.Connection, name: str):
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
        pass  # TODO

    def __iter__(self) -> Iterator[str]:
        pass  # TODO

    def __getitem__(self, key: str) -> Any:
        pass  # TODO

    def __delitem__(self, key: str) -> None:
        pass  # TODO

    def __setitem__(self, key: str, value: Any) -> None:
        pass  # TODO

    def __enter__(self) -> Collection:
        """
        Enter a transaction.
        """
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Leave current transaction.
        """
        self.connection.__exit__(exc_type, exc_value, traceback)


class Connection(ConnectionWrapper, AbstractContextManager, MutableMapping[str, Collection]):
    """
    Represents a connection and wraps a standard SQLite connection.
    Provides the dictionary interface to collections.
    """

    def __init__(self, database: Union[str, bytes, PathLike], **kwargs: Any):
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
        return Collection(self.connection, name)

    def __setitem__(self, name: str, value: Collection) -> None:
        raise TypeError('setting an entire collection is not supported')

    def __delitem__(self, name: str) -> None:
        """
        Drop a collection.
        """
        if not table_name_re.match(name):
            raise ValueError(f'incorrect table name: {name}')
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute(f'DROP TABLE `{name}`')
        except sqlite3.OperationalError as e:
            raise KeyError(name) from e

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Close the connection.
        """
        self.close()

    def close(self):
        """
        Close the connection.
        """
        self.connection.close()
