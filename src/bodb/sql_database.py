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
from sqlalchemy.exc import NoSuchTableError
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
        Base = declarative_base()
        _FunctionEvaluation = _new_feval_class(
            Base,
            self.tablename,
            {key: type(value) for key, value in evaluation.items()},
        )
        with self._session() as session:
            Base.metadata.create_all(session.bind)
            session.add(_FunctionEvaluation(**evaluation))
        return self

    def extend(self, iterable):
        # Base = declarative_base()
        # _FunctionEvaluation = _new_feval_class(
        #     Base,
        #     self.tablename,
        #     {key: type(value) for key, value in evaluation.items()},
        # )
        # with self._session() as session:
        #     Base.metadata.create_all(session.bind)
        #     objects = map(lambda d: _FunctionEvaluation(**d), iterable)
        #     session.add_all(objects)
        for item in iterable:
            self.append(item)
        return self

    def __len__(self):
        with self._session() as session:
            table = self._reflected_table(session)
            length = 0 if table is None else session.query(table).count()
        return length

    def __getitem__(self, key):
        with self._session() as session:
            table = self._reflected_table(session)
            result = session.query(table).filter(table.columns["_id"] == key).one()
            return mapped_to_dict(table, result)

    # def __contains__(self, evaluation):
    #     with self._session() as session:
    #         return session.query(self._FunctionEvaluation).one_or_none() is not None

    def __iter__(self):
        with self._session() as session:
            table = self._reflected_table(session)
            items = (
                iter([])
                if table is None
                else iter([mapped_to_dict(table, e) for e in session.query(table)])
            )
        return items

    @contextmanager
    def _session(self):
        with _engine_scope(create_engine(self.uri)) as engine:
            with _session_scope(Session(bind=engine)) as session:
                yield session

    def _reflected_table(self, session):
        try:
            table = Table(
                self.tablename, MetaData(), autoload=True, autoload_with=session.bind
            )
        except NoSuchTableError:
            return None

        return table


def mapped_to_dict(table, mapped):
    return {
        attr: getattr(mapped, attr) for attr in table.columns.keys() if attr != "_id"
    }


@contextmanager
def _engine_scope(engine):
    yield engine


@contextmanager
def _session_scope(session):
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

    new_type = type(
        "FunctionEvaluation",
        (Base,),
        {"__tablename__": tablename, "_id": id_column, **columns,},
    )

    return new_type
