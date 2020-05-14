from contextlib import contextmanager
from typing import get_type_hints

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SA_TYPE_MAP = {
    float: sa.Float,
    int: sa.Integer,
    str: sa.Text(),
    bool: sa.Boolean,
}


class Database:
    def __init__(self, uri, func_name, func):
        self._engine = sa.create_engine(uri)
        self._Session = sessionmaker(bind=self._engine)
        self._Base = declarative_base()
        self._FunctionEvaluation = _class_from_func(self._Base, func_name, func)
        with self._session() as session:
            self._Base.metadata.create_all(session.bind)

    def register(self, point, target):
        with self._session() as session:
            session.add(self._FunctionEvaluation(**point, target=target))

    def count(self):
        with self._session() as session:
            return session.query(self._FunctionEvaluation).count()

    def all(self):
        with self._session() as session:
            return [
                e.to_point_target() for e in session.query(self._FunctionEvaluation)
            ]

    def _session(self):
        return _session_scope(self._Session)


@contextmanager
def _session_scope(Session):
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def _class_from_func(Base, func_name, func):
    tablename = func_name

    type_hints = get_type_hints(func)
    target_type = type_hints.pop("return")
    params = type_hints

    param_columns = {
        param_name: sa.Column(SA_TYPE_MAP[param_type], nullable=False)
        for param_name, param_type in params.items()
    }

    def to_point_target(self):
        return (
            {param_name: getattr(self, param_name) for param_name in type_hints},
            self.target,
        )

    id_column = sa.Column(sa.Integer, primary_key=True)
    target_column = sa.Column(SA_TYPE_MAP[target_type], nullable=False)

    new_type = type(
        "FunctionEvaluation",
        (Base,),
        {
            "__tablename__": tablename,
            "id": id_column,
            **param_columns,
            "target": target_column,
            "to_point_target": to_point_target,
        },
    )

    return new_type
