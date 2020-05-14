from contextlib import contextmanager
import sys
from time import sleep
from typing import get_type_hints

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction


@contextmanager
def session_scope(*args, **kwargs):
    """Provide a transactional scope around a series of operations."""
    session = sessionmaker(*args, **kwargs)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


SA_TYPE_MAP = {
    float: sa.Float,
    int: sa.Integer,
    str: sa.Text(),
}


def class_from_func(func):
    Base = declarative_base()
    tablename = func.__name__ + "_evaluations"

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


def black_box_function(x: float, y: float) -> float:
    print(f"Evaluating ({x}, {y})...")
    sleep(1)
    target = -(x ** 2) - (y - 1) ** 2 + 1
    print(f"Got {target}")
    return target


PBOUNDS = {"x": (2, 4), "y": (-3, 3)}

INITIAL_POINTS = [
    {"x": 0, "y": 0},
    {"x": 1, "y": 2},
]


def main(args):
    engine = sa.create_engine("sqlite:///test.db")
    FunctionEvaluation = class_from_func(black_box_function)

    optimizer = BayesianOptimization(f=None, pbounds=PBOUNDS, random_state=1,)
    utility_function = UtilityFunction(kind="ucb", kappa=3, xi=1)

    with session_scope(bind=engine) as session:
        Base.metadata.create_all(engine)  # Create table if it doesn't exist

        query = session.query(FunctionEvaluation)

        if query.count() < 2:  # Check if there are enough existing datapoints
            initial_targets = []
            for point in INITIAL_POINTS:
                target = black_box_function(**point)
                with session.begin_nested():
                    session.add(FunctionEvaluation(**point, target=target))

        for evaluation in query:
            point, target = evaluation.to_point_target()
            optimizer.register(point, target)

        while True:
            try:
                point = optimizer.suggest(utility_function)
                target = black_box_function(**point)
                with session.begin_nested():
                    session.add(FunctionEvaluation(**point, target=target))
                optimizer.register(point, target)
            except KeyboardInterrupt:
                break

    return 0


if __name__ == "__main__":
    exit(main(sys.argv))
