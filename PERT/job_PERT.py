import matplotlib.pyplot as plt
import numpy as np
from scipy.special import betaincinv
from CPM import Job

class PJob(Job):
    def __init__(self, id, optimistic, most_likely, pessimistic, predecessors, is_dummy=False, prev_state=None) -> None:
        duration = self.pert_duration(optimistic, most_likely, pessimistic)
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
        alpha = 1 + 4 * (most_likely-optimistic) / (pessimistic-optimistic)
        beta = 1 + 4 * (pessimistic-most_likely) / (pessimistic - optimistic)
        z = betaincinv(alpha, beta, np.random.uniform(0, 1))
        return optimistic + z * (pessimistic - optimistic)


class OJob(Job):
    def __init__(self, id, optimistic, most_likely, pessimistic, predecessors, is_dummy=False, prev_state=None) -> None:
        super().__init__(id, most_likely, predecessors, is_dummy, prev_state)

if __name__ == '__main__':
    optimistic = 2
    most_likely = 5
    pessimistic = 7
    durations = []
    for i in range(1000000):
        durations.append(PJob.beta_duration(optimistic, most_likely, pessimistic))
    plt.plot()
    plt.hist(durations)
    plt.show()
