import time

from bodb import Database

from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction


def black_box_function(x: float, y: float) -> float:
    print(f"Evaluating ({x}, {y})...")
    time.sleep(1)
    target = -(x ** 2) - (y - 1) ** 2 + 1
    print(f"Got {target}")
    return target


PBOUNDS = {"x": (2, 4), "y": (-3, 3)}

INITIAL_POINTS = [
    {"x": 0, "y": 0},
    {"x": 1, "y": 2},
]


database = Database("sqlite:///test.db", black_box_function)
optimizer = BayesianOptimization(f=None, pbounds=PBOUNDS, random_state=1,)
utility_function = UtilityFunction(kind="ucb", kappa=3, xi=1)

if database.count() < 2:  # Check if there are enough existing datapoints
    initial_targets = []
    for point in INITIAL_POINTS:
        target = black_box_function(**point)
        database.register(point, target)

for (point, target) in database.all():
    optimizer.register(point, target)

while True:
    try:
        point = optimizer.suggest(utility_function)
        target = black_box_function(**point)
        database.register(point, target)
        optimizer.register(point, target)
    except KeyboardInterrupt:
        break
