import time

from bodb import Database

from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction


def black_box_function(x: float, y: float) -> float:
    time.sleep(1)
    target = -(x ** 2) - (y - 1) ** 2 + 1
    return target


pbounds = {"x": (2, 4), "y": (-3, 3)}

initial_points = [
    {"x": 0, "y": 0},
    {"x": 1, "y": 2},
]

print("Connecting to database...")
database = Database("sqlite:///test.db", "my_function", black_box_function)

print("Creating optimizer and utility function...")
optimizer = BayesianOptimization(f=None, pbounds=pbounds, random_state=1,)
utility_function = UtilityFunction(kind="ucb", kappa=3, xi=1)

print("Checking existing number of evaluations...")
if database.count() < 2:  # Check if there are enough existing datapoints
    initial_targets = []
    for point in inital_points:
        target = black_box_function(**point)
        database.register(point, target)

print("Registering evaluations with optimizer...")
for (point, target) in database.all():
    optimizer.register(point, target)

while True:
    try:
        point = optimizer.suggest(utility_function)
        print(f"Evaluating black-box function for {point}")
        target = black_box_function(**point)
        print(f"Got {target}")
        print("Registering with database...")
        database.register(point, target)
        print("Registering with optimizer...")
        optimizer.register(point, target)
    except KeyboardInterrupt:
        print("Exiting...")
        break