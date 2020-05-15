import time

from bodb import SQLDatabase

from bayes_opt import BayesianOptimization
from bayes_opt.util import UtilityFunction


def black_box_function(x, y):
    time.sleep(1)
    target = -(x ** 2) - (y - 1) ** 2 + 1
    return target


arg_types = {
    "x": float,
    "y": float,
}

return_type = float

pbounds = {"x": (2, 4), "y": (-3, 3)}

initial_points = [
    {"x": 0, "y": 0},
    {"x": 1, "y": 2},
]

print("Connecting to database...")
database = SQLDatabase("sqlite:///test.db", "my_function", arg_types, return_type)

print("Checking existing number of evaluations...")
if len(database) < 2:  # Check if there are enough existing datapoints
    initial_targets = []
    for point in initial_points:
        target = black_box_function(**point)
        database.add((point, target))

print("Creating optimizer and utility function...")
optimizer = BayesianOptimization(f=None, pbounds=pbounds, random_state=1)

utility_funcs = [
    UtilityFunction(kind="ucb", kappa=3, xi=1),
    ...,
]

print("Registering evaluations with optimizer...")
for (point, target) in database:
    optimizer.register(point, target)

while True:
    try:
        points = []
        for uf in utility_funcs:
            points.append(optimizer.suggest(uf))

        create_slurm_job(points)
        run_job()
        read_results_from_job()

        # print(f"Evaluating black-box function for {point}")
        # target = black_box_function(**point)
        # print(f"Got {target}")
        # print("Registering with database...")
        for point, target in results:
            database.add((point, target))
            print("Registering with optimizer...")
            optimizer.register(point, target)
    except KeyboardInterrupt:
        print("Exiting...")
        break
