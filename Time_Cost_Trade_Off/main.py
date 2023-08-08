import pandas as pd
from Optimizer import Optimizer
from Jobs import *
import os
PATH = os.path.dirname(os.path.realpath(__file__))

def main(filepath, visualize=False) -> None:
    c0 = 6
    workflow = pd.read_csv(filepath+'/workflow.csv')
    costs = pd.read_csv(filepath+'/costs.csv')
    jobs = create_jobs(workflow, costs)
    oz = Optimizer(jobs, c0)
    critical_path, makespan = oz.optimize(visualize=visualize)
    print()
    print_jobs(list(jobs.values()))
    print('critical_paths:')
    for path in oz.critical_paths:
        print(end='  ')
        print_path(path)
    print(f'total_cost: {total_cost(list(jobs.values()))}')
    print(f'makespan: {makespan}\n')

if __name__== '__main__':
    main(PATH+'/input/pinedo_4_4', visualize=False)
