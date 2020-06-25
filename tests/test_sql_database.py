import pickle
from tempfile import mkstemp

from bodb import SQLDatabase

import pytest


# class TestInit:
#     @pytest.mark.parametrize("arg_types, return_type", [({"x": int}, int)])
#     def test_types(self, arg_types, return_type):
#         SQLDatabase("sqlite://", "test", arg_types, return_type)


@pytest.fixture
def sql_database_factory(tmp_path):
    def factory():
        _, path = mkstemp(suffix=".db", dir=tmp_path)
        uri = f"sqlite:///{path}"
        return SQLDatabase(uri, "my_table")

    return factory


@pytest.fixture
def sql_database(sql_database_factory):
    return sql_database_factory()


def test_new_len(sql_database):
    assert len(sql_database) == 0


@pytest.mark.parametrize(
    "item",
    [{"x": 1}, {"x": 1, "y": 2}, {"x": 1, "y": 2.0}, {"x": 1, "y": 2.0, "z": "hello"}],
)
def test_append_iter(sql_database, item):
    assert list(sql_database.append(item)) == [item]


@pytest.mark.parametrize(
    "items", [[{"x": 1}, {"x": 1}], [{"x": 1.2}, {"x": 1}]],
)
def test_extend_iter(sql_database, items):
    assert list(sql_database.extend(items)) == items


@pytest.mark.parametrize("items", [[{"x": 1}], [{"x": 1}, {"x": 2}]])
def test_create_length(sql_database, items):
    assert len(sql_database.extend(items)) == len(items)


def test_append_getitem(sql_database):
    assert sql_database.append({"x": 1})[1] == {"x": 1}


def test_weird_type(sql_database):
    class MyInt(int):
        pass

    sql_database.append({"x": MyInt(2)})


# def test_extend_getitem_slice(sql_database):
#     assert sql_database.extend([{"x": 0}, {"x": 1})[1] == {"x": 1}


@pytest.mark.parametrize("items", [[], [{"x": 1}]])
def test_equality(sql_database_factory, items):
    table1 = sql_database_factory()
    table2 = sql_database_factory()
    table1.extend(items)
    table2.extend(items)
    assert table1 == table2


def test_picklable(sql_database):
    sql_database.append({"x": 1})
    assert pickle.loads(pickle.dumps(sql_database)) == sql_database
