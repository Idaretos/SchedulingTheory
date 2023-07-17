from CPM import Job
import numpy as np

class PJob(Job):
    def __init__(self, id, optimistic, normal, pessimistic, predecessors, is_dummy=False, prev_state=None) -> None:
        duration = calculate_duration(optimistic, normal, pessimistic)
        super().__init__(id, duration, predecessors, is_dummy, prev_state)

def calculate_duration(optimistic, normal, pessimistic):
    mean = (optimistic + 4*normal + pessimistic)/6
    std_dev = np.absolute((pessimistic-optimistic)/6)
    duration = np.random.normal(mean, std_dev)
    if duration < optimistic:
        duration = optimistic
    elif duration > pessimistic:
        duration = pessimistic
    return duration

