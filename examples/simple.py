import time

from bodb import SQLDatabase
import click
from toolz.dicttoolz import dissoc

from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction


def black_box_function(x, y):
    time.sleep(1)
    target = -(x ** 2) - (y - 1) ** 2 + 1
    return target


pbounds = {"x": (2, 4), "y": (-3, 3)}

initial_points = [
    {"x": 0, "y": 0},
    {"x": 1, "y": 2},
]


@click.command()
@click.argument("db_uri")
@click.argument("tablename")
def main(db_uri, tablename):
    click.echo("Connecting to database...")
    database = SQLDatabase(db_uri, tablename)

    click.echo("Checking existing number of evaluations...")
    if len(database) < 2:  # Check if there are enough existing datapoints
        for point in initial_points:
            target = black_box_function(**point)
            database.append({**point, "target": target})

    click.echo("Creating optimizer and utility function...")
    optimizer = BayesianOptimization(f=None, pbounds=pbounds, random_state=1)
    utility_function = UtilityFunction(kind="ucb", kappa=3, xi=1)

    click.echo("Registering evaluations with optimizer...")
    for evaluation in database:
        optimizer.register(dissoc(evaluation, "target"), evaluation["target"])

    while True:
        try:
            point = optimizer.suggest(utility_function)
            click.echo(f"Evaluating black-box function for {point}")
            target = black_box_function(**point)
            click.echo(f"Got {target}")
            click.echo("Registering with database...")
            database.append({**point, "target": target})
            click.echo("Registering with optimizer...")
            optimizer.register(point, target)
        except KeyboardInterrupt:
            click.echo("Exiting...")
            break


if __name__ == "__main__":
    main()
