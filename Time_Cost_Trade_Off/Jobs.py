from collections import defaultdict
from typing import Tuple, List, Dict
import ast

class Job(object):
    def __init__(self, id, predecessors, p_max, p_min, cost, marginal_cost, is_dummy=False, prev_state=None) -> None:
        self.id = str(id)
        self.duration = p_max
        self.predecessors = [str(predecessor) for predecessor in predecessors]
        self.p_max = p_max
        self.p_min = p_min
        self.cost = cost
        self.marginal_cost = marginal_cost
        self.is_dummy = is_dummy
        if self.is_dummy:
            self.prev_state = prev_state

    def __repr__(self) -> str:
        return self.id
    
    def __lt__(self, other):
        if isinstance(other, Job):
            return self.id < other.id
        return False

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, Job):
            return self.id > other.id
        return False

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)


    
def create_jobs(workflow, costs) -> Dict[str, Job]:
    workflow['predecessors'] = workflow['predecessors']
    ids = workflow['id'].tolist()
    predecessors = workflow['predecessors'].tolist()
    p_maxs = costs['p_max'].tolist()
    p_mins = costs['p_min'].tolist()
    min_costs = costs['curr_cost'].tolist()
    marginal_costs = costs['marginal_cost'].tolist()
    jobs = {}
    for i in range(len(ids)):
        jobs[str(ids[i])] = Job(str(ids[i]), predecessors[i], p_maxs[i], p_mins[i], curr_costs[i], marginal_costs[i])
    return jobs


def print_path(path: List[Job]) -> None:
    print('source -> ', end='')
    for job in path:
        print(job.id, end=' -> ')
    print('sink')

def print_path_indetail(path: List[Job]) -> None:
    print('job:', end='\t')
    for job in path:
        print(job.id, end='\t')
    print('\np_max:', end='\t')
    for job in path:
        print(job.p_max, end='\t')
    print('\np_min:', end='\t')
    for job in path:
        print(job.p_min, end='\t')
    print('\ncost:', end='\t')
    for job in path:
        print(job.cost+job.marginal_cost*(job.duration-job.p_min), end='\t')
    print('\nmarg:', end='\t')
    for job in path:
        print(job.marginal_cost, end = '\t')
    print('\ndur:', end='\t')
    for job in path:
        print(job.duration, end='\t')
    print()

def print_jobs(jobs: List[Job]) -> None:
    print('job:', end='\t')
    for job in jobs:
        print(job.id, end='\t')
    print('\np_max:', end='\t')
    for job in jobs:
        print(job.p_max, end='\t')
    print('\np_min:', end='\t')
    for job in jobs:
        print(job.p_min, end='\t')
    print('\ncost:', end='\t')
    for job in jobs:
        print(job.cost+job.marginal_cost*(job.duration-job.p_min), end='\t')
    print('\nmarg:', end='\t')
    for job in jobs:
        print(job.marginal_cost, end = '\t')
    print('\ndur:', end='\t')
    for job in jobs:
        print(job.duration, end='\t')
    print()

def total_cost(jobs: List[Job]) -> float:
    sum = 0
    for job in jobs:
        sum += job.cost+job.marginal_cost*(job.duration-job.p_min)
    return sum


class Network:
    def __init__(self, jobs: Dict[str, Job]) -> None:
        '''
        parameters:
        jobs: dictionary of jobs.
        '''
        self.jobs = list(jobs.values())
        self.predecessors = defaultdict(list)
        self.successors = defaultdict(list)
        for job in self.jobs:
            try:
                self.predecessors[job.id] += [jobs[id] for id in job.predecessors]
                for predecessor_id in job.predecessors:
                    self.successors[predecessor_id].append(job)
            except KeyError:
                pass
        self.sources = []
        self.sinks = []
        self.sort()

    def sort(self) -> None:
        self.sources, self.sinks, self.jobs = topological_sort(self.jobs, self.successors)

    def get_jobs(self) -> List[Job]:
        return self.jobs

def topological_sort(jobs, successors) -> Tuple[list, list, list]:
    in_degree = defaultdict(int)
    sorted_order = []

    # Calculate in-degree for each job
    for job in jobs:
        for successor in successors[job.id]:
            in_degree[successor.id] += 1

    # Find jobs with no incoming edges (in-degree = 0)
    sources = [job for job in jobs if job.id not in in_degree or in_degree[job.id] == 0]
    sources_to_return = [job for job in jobs if job.id not in in_degree or in_degree[job.id] == 0]
    sinks = []

    # Perform topological sort
    while sources:
        job = sources.pop(0)
        sorted_order.append(job)

        # Decrement the in-degree of each successor and add to sources if in-degree becomes 0
        for successor in successors[job.id]:
            in_degree[successor.id] -= 1
            if in_degree[successor.id] == 0:
                sources.append(successor)

        # Check if the job is a sink (no outgoing edges)
        if job.id not in successors or len(successors[job.id]) == 0:
            sinks.append(job)

    return sources_to_return, sinks, sorted_order
