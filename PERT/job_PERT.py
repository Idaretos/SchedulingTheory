import matplotlib.pyplot as plt
import numpy as np
import sys
from os.path import dirname, realpath
from scipy.special import betaincinv
from CPM import Job

class PJob(Job):
    def __init__(self, id, optimistic, most_likely, pessimistic, predecessors, is_dummy=False, prev_state=None) -> None:
        duration = self.normal_duration(optimistic, most_likely, pessimistic)
        super().__init__(id, duration, predecessors, is_dummy, prev_state)

    @staticmethod
    def normal_duration(optimistic, most_likely, pessimistic) -> float:
        mean = (optimistic + 4*most_likely + pessimistic)/6
        std_dev = np.absolute((pessimistic-optimistic)/6)
        duration = np.random.normal(mean, std_dev)
        if duration < optimistic:
            duration = optimistic
        elif duration > pessimistic:
            duration = pessimistic
        return duration
    
    @staticmethod
    def beta_duration(optimistic, most_likely, pessimistic) -> float:
        return optimistic + np.random.beta(np.max((most_likely-optimistic, 0.0001)), pessimistic-most_likely)*(pessimistic-optimistic)
    
    @staticmethod
    def pert_duration(optimistic, most_likely, pessimistic) -> float:
        if pessimistic == optimistic:
            return most_likely
        alpha = 1 + 4 * (most_likely-optimistic) / (pessimistic-optimistic)
        beta = 1 + 4 * (pessimistic-most_likely) / (pessimistic - optimistic)
        z = betaincinv(alpha, beta, np.random.uniform(0, 1))
        beta_param = 1 + 4 * (pessimistic - most_likely) / (pessimistic - optimistic)
        z = beta.ppf(np.random.uniform(0, 1), alpha, beta_param)
        return optimistic + z * (pessimistic - optimistic)


class OJob(Job):
    def __init__(self, id, optimistic, most_likely, pessimistic, predecessors, is_dummy=False, prev_state=None) -> None:
        super().__init__(id, most_likely, predecessors, is_dummy, prev_state)

def arg():
    inputpath = dirname(realpath(__file__))+'/input/example.csv'
    outputpath = dirname(realpath(__file__))+'/output'
    threshold = None
    if len(sys.argv) > 1:
        inputpath = sys.argv[1]
    if len(sys.argv) > 2:
        outputpath = sys.argv[2]
    if len(sys.argv) > 3:
        threshold = int(sys.argv[3])
    return inputpath, outputpath, threshold