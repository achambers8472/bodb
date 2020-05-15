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


class SQLDatabase:
    def __init__(self, uri, tablename, arg_types, return_type):
        _engine = sa.create_engine(uri)
        self._Session = sessionmaker(bind=_engine)
        _Base = declarative_base()
        self._FunctionEvaluation = _new_feval_class(
            _Base, tablename, arg_types, return_type
        )
        with self._session() as session:
            _Base.metadata.create_all(session.bind)

    def add(self, evaluation):
        with self._session() as session:
            session.add(self._FunctionEvaluation.from_evaluation(evaluation))

    def __len__(self):
        with self._session() as session:
            return session.query(self._FunctionEvaluation).count()

    def __iter__(self):
        with self._session() as session:
            return iter(
                [e.to_evaluation() for e in session.query(self._FunctionEvaluation)]
            )

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


def _new_feval_class(Base, tablename, arg_types, return_type):
    id_column = sa.Column(sa.Integer, primary_key=True)

    arg_columns = {
        name: sa.Column(SA_TYPE_MAP[type], nullable=False)
        for name, type in arg_types.items()
    }
    return_column = sa.Column(SA_TYPE_MAP[return_type], nullable=True)

    @classmethod
    def from_evaluation(cls, evaluation):
        return cls(**evaluation[0], target=evaluation[1])

    def to_evaluation(self):
        return (
            {name: getattr(self, name) for name in arg_types},
            self.target,
        )

    new_type = type(
        "FunctionEvaluation",
        (Base,),
        {
            "__tablename__": tablename,
            "id": id_column,
            "from_evaluation": from_evaluation,
            "to_evaluation": to_evaluation,
            **arg_columns,
            "target": return_column,
        },
    )

    return new_type
