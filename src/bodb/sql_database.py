from contextlib import contextmanager
from typing import get_type_hints

from sqlalchemy import (
    create_engine,
    Column,
    Float,
    Integer,
    Text,
    Boolean,
    MetaData,
    func,
    select,
    Table,
)
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base


SA_TYPE_MAP = {
    float: Float,
    int: Integer,
    str: Text(),
    bool: Boolean,
}


class SQLDatabase:
    def __init__(self, uri, tablename):
        self.uri = uri
        self.tablename = tablename

    def append(self, evaluation):
        with _engine_scope(self.uri) as engine:
            Base = declarative_base()
            _FunctionEvaluation = _new_feval_class(
                Base,
                self.tablename,
                {key: type(value) for key, value in evaluation.items()},
            )
            with _session_scope(engine) as session:
                Base.metadata.create_all(session.bind)
                session.add(_FunctionEvaluation(**evaluation))
        return self

    def extend(self, iterable):
        for item in iterable:
            self.append(item) 
        return self

    def __len__(self):
        with _engine_scope(self.uri) as engine:
            meta = MetaData()
            table = Table(self.tablename, meta, autoload=True, autoload_with=engine)
            with _session_scope(engine) as session:
                return session.query(table).count()

    def __getitem__(self, key):
        with _engine_scope(self.uri) as engine:
            meta = MetaData()
            table = Table(self.tablename, meta, autoload=True, autoload_with=engine)
            with _session_scope(engine):
                return session.query(table).filter(table.columns._id == key).one()

    # def __contains__(self, evaluation):
    #     with self._session() as session:
    #         return session.query(self._FunctionEvaluation).one_or_none() is not None

    def __iter__(self):
        with _engine_scope(self.uri) as engine:
            meta = MetaData()
            table = Table(self.tablename, meta, autoload=True, autoload_with=engine)
            with _session_scope(engine) as session:
                return iter(
                    [
                        {
                            name: getattr(e, name)
                            for name in table.columns.keys()
                            if name != "_id"
                        }
                        for e in session.query(table)
                    ]
                )


@contextmanager
def _engine_scope(uri):
    yield create_engine(uri)


@contextmanager
def _session_scope(engine):
    session = Session(bind=engine)
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def _new_feval_class(Base, tablename, types):
    id_column = Column(Integer, primary_key=True)

    columns = {
        name: Column(SA_TYPE_MAP[type], nullable=False) for name, type in types.items()
    }

    def to_evaluation(self):
        return

    new_type = type(
        "FunctionEvaluation",
        (Base,),
        {"__tablename__": tablename, "_id": id_column, **columns,},
    )

    return new_type
