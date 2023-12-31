from collections import defaultdict
import numpy as np

class Job:
    def __init__(self, id, duration, predecessors, is_dummy=False, prev_state=None) -> None:
        self.id = id
        self.duration = duration
        self.predecessors = [str(predecessor) for predecessor in predecessors]
        self.is_dummy = is_dummy
        if self.is_dummy:
            self.prev_state = prev_state

    def __repr__(self) -> str:
        return self.id
    
    def __eq__(self, other):
        if isinstance(other, Job):
            return (self.id == other.id
                    and self.duration == other.duration
                    and self.predecessors == other.predecessors
                    and self.is_dummy == other.is_dummy)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

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
    
    def __hash__(self):
        return hash(self.id)


class Network:
    def __init__(self, jobs) -> None:
        '''
        parameters:
        jobs: dictionary of jobs.
        '''
        self.jobs = list(jobs.values())
        self.predecessors = defaultdict(list)
        self.successors = defaultdict(list)
        for job in self.jobs:
            self.predecessors[job.id] += [jobs[i] for i in job.predecessors]
            for predecessor_id in job.predecessors:
                self.successors[predecessor_id].append(job)
        self.sources = []
        self.sinks = []
        self.sort()
        self.paths = self.all_paths()
        self.critical_paths = []

    def all_paths(self) -> list:
        def dfs(current, path):
            # If the current job is a sink, add the path to the result
            if current in self.sinks:
                paths.append(path)
                return
            
            # Explore the successors of the current job
            for successor in self.successors[current.id]:
                dfs(successor, path + [successor])

        paths = []
        # Start DFS from each source in the network
        for source in self.sources:
            dfs(source, [source])

        return paths

    def sort(self) -> None:
        self.sources, self.sinks, self.jobs = topological_sort(self.jobs, self.successors)

    def get_jobs(self) -> list:
        return self.jobs

    def get_predecessors(self) -> defaultdict:
        return self.predecessors
    
    def get_successors(self) -> defaultdict:
        return self.successors

def topological_sort(jobs, successors) -> tuple:
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

def calculate_earliest_times(network) -> tuple:
    jobs = network.get_jobs()
    predecessors = network.get_predecessors()

    earliest_start_time = {}
    earliest_finish_time = {}

    # Calculate earliest start and finish times
    for job in network.sources:
        earliest_start_time[job.id] = 0  # Initialize earliest start time to 0

    for job in jobs:
        if job in network.sources:
            # Job has no dependencies, set earliest finish time to its duration
            earliest_finish_time[job.id] = job.duration
        else:
            # Calculate earliest finish time as the maximum of earliest finish times of dependent jobs
            earliest_start_time[job.id] = max(earliest_finish_time[predecessor.id] for predecessor in predecessors[job.id])
            earliest_finish_time[job.id] = earliest_start_time[job.id] + job.duration

    return earliest_start_time, earliest_finish_time


def calculate_latest_times(network, earliest_finish_time) -> tuple:
    jobs = network.get_jobs()
    successors = network.get_successors()

    latest_start_time = {}
    latest_finish_time = {}

    project_duration = max(earliest_finish_time.values())

    # Calculate latest start and finish times
    for job in network.sinks:
        latest_finish_time[job.id] = project_duration  # Initialize latest finish time to project duration
        latest_start_time[job.id] = project_duration - job.duration

    jobs.reverse()
    for job in jobs:
        # Calculate latest start time as the minimum of latest start times of dependent jobs
        if job in network.sinks:
            continue
        else:
            latest_finish_time[job.id] = min(latest_start_time[successor.id] for successor in successors[job.id])
            latest_start_time[job.id] = latest_finish_time[job.id] - job.duration
    
    return dict(reversed(list(latest_start_time.items()))),  dict(reversed(list(latest_finish_time.items())))


def calculate_slacks(jobs, earliest_start_time, latest_start_time) -> dict:
    slacks = {}
    for job in jobs:
        slack_time = latest_start_time[job.id] - earliest_start_time[job.id]
        slacks[job] = slack_time
    return slacks


def calculate_critical_path(slacks) -> list:
    critical_path = [job for job, slack_time in slacks.items() if np.round(slack_time, 1) == 0.0]
    return sorted(critical_path, key=(lambda x : int(x.id)))


def CPM(network) -> tuple:
    earliest_start_time, earliest_finish_time = calculate_earliest_times(network)
    latest_start_time, latest_finish_time = calculate_latest_times(network, earliest_finish_time)
    slacks = calculate_slacks(network.jobs, earliest_start_time, latest_start_time)
    critical_path = calculate_critical_path(slacks)
    makespan = max(earliest_finish_time.values())
    for path in network.paths:
        tmp_span = 0
        for job in path:
            tmp_span += job.duration
        if tmp_span == makespan:
            network.critical_paths.append(path)
    return earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan
