from preprocessing import *
from Optimizer import Optimizer

if __name__== '__main__':
    filepath, rule, v = arg()
    workflow, costs, c0 = read_files(filepath)
    oz = Optimizer(workflow, costs, c0)
    oz.optimize(rule, v)
    oz.show()
