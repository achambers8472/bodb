from bodb import SQLDatabase

import pytest


# class TestInit:
#     @pytest.mark.parametrize("arg_types, return_type", [({"x": int}, int)])
#     def test_types(self, arg_types, return_type):
#         SQLDatabase("sqlite://", "test", arg_types, return_type)


@pytest.fixture
def sql_database(tmp_path):
    return SQLDatabase(f"sqlite:///{tmp_path/'test.db'}", "test")


class TestAdd:
    @pytest.mark.parametrize(
        "item",
        [
            {"x": 1},
            {"x": 1, "y": 2},
            {"x": 1, "y": 2.0},
            {"x": 1, "y": 2.0, "z": "hello"},
        ]
    )
    def test_create_read(self, sql_database, item): 
        assert list(sql_database.append(item)) == [item]

    @pytest.mark.parametrize(
        "items",
        [
            [{"x": 1}],
            [{"x": 1}, {"x": 2}],
        ]
    )
    def test_create_length(self, sql_database, items):
        assert len(sql_database.extend(items)) == len(items)

