# See also: https://stackoverflow.com/questions/3694276/what-are-valid-table-names-in-sqlite
good_table_names = [
    'foo',
    '123abc',
    '123abc.txt',
    '123abc-ABC.txt',
    'foo""bar',
    '😀',
    '_sqlite',
]

# See also: https://stackoverflow.com/questions/3694276/what-are-valid-table-names-in-sqlite
bad_table_names = [
    '"',
    '"foo"',
    'sqlite_',
    'sqlite_reserved',
]
