from preprocessing import *
from Optimizer import Optimizer

if __name__== '__main__':
    filepath, rule, v = arg(PATH+'/input/lecture', 'heuristic', False) 
    # for example: python main.py 'input' 'heuristic' 'True'
    # filepath = 'input' (should include costs.csv, workflow.csv)
    # rule = 'heuristic' or 'lp'
    # v = True
    workflow, costs, c0 = read_files(filepath)
    oz = Optimizer(workflow, costs, c0)
    oz.optimize(rule, v)
    oz.show()
