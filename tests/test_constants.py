from pytest import mark
from tests.constants import bad_table_names, good_table_names

from sqlitemap import table_name_re


@mark.parametrize('name', good_table_names)
def test_valid_table_name(name: str):
    assert table_name_re.match(name)


@mark.parametrize('name', bad_table_names)
def test_invalid_table_name(name: str):
    assert not table_name_re.match(name)
