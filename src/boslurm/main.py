def step():
    points, targets = read_data(database)
    new_point = bayes_opt(pars, points, targets)
    new_target = black_box_func(new_point)
    update_data(points, targets)


def read_data(database):
    pass


def bayesian_optimisation(parameters, points, targets) -> :
    pass

