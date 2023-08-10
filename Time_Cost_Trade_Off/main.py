from preprocessing import *
from Optimizer import Optimizer

def main(filepath, rule='heuristic', v=False) -> None:
    workflow, costs, c0 = read_files(filepath)
    oz = Optimizer(workflow, costs, c0)
    oz.optimize(rule, v)
    oz.show()

if __name__== '__main__':
    main(PATH+'/input/example', rule='heuristic', v=True)
