from bodb import SQLDatabase

import pytest


class TestInit:
    @pytest.mark.parametrize("arg_types, return_type", [({"x": int}, int)])
    def test_types(self, arg_types, return_type):
        SQLDatabase("sqlite://", "test", arg_types, return_type)


class TestAdd:
    def test_simple(self):
        pass
