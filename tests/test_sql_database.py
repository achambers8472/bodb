from bodb import SQLDatabase

import pytest


# class TestInit:
#     @pytest.mark.parametrize("arg_types, return_type", [({"x": int}, int)])
#     def test_types(self, arg_types, return_type):
#         SQLDatabase("sqlite://", "test", arg_types, return_type)


@pytest.fixture
def sql_database(tmp_path):
    return SQLDatabase(f"sqlite:///{tmp_path/'test.db'}", "test")


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


# def test_extend_getitem_slice(sql_database):
#     assert sql_database.extend([{"x": 0}, {"x": 1})[1] == {"x": 1}
