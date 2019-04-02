# `0.2.0`

- Change: #1 `Connection.__getitem__` now uses a cache for `Collection`s. Repeated calls return the same `Collection` instance. Note: don't delete collections which may be used by other processes

# `0.1.1`

- Allow more [valid SQLite table names](https://stackoverflow.com/questions/3694276/what-are-valid-table-names-in-sqlite)
- Improve `README`
- Add `mypy` checks

# `0.1.0`

- Initial release
