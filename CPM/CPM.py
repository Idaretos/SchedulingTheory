from collections import defaultdict
from copy import deepcopy


class Job:
    def __init__(self, id, duration, predecessors):
        self.id = id
        self.duration = duration
        self.predecessors = predecessors

    def __repr__(self):
        return self.id


class Network:
    def __init__(self, jobs):
        '''
        parameters:
        jobs: dictionary of jobs.
        '''
        self.jobs = jobs.values()
        self.predecessors = defaultdict(list)
        self.successors = defaultdict(list)
        for job in self.jobs:
            self.predecessors[job] += [jobs[i] for i in job.predecessors]
            for predecessor in job.predecessors:
                self.successors[predecessor].append(job)
        self.sources = []
        self.sinks = []
        self.sort()

    def add_job(self, job):
        self.jobs.append(job)

    def add_dependency(self, successor, predecessor):
        self.predecessors[successor].append(predecessor)
        self.successors[predecessor].append(successor)

    def sort(self):
        self.sources, self.sinks, self.jobs = topological_sort(self.jobs, self.successors)

    def get_jobs(self):
        return self.jobs

    def get_predecessors(self):
        return self.predecessors
    
    def get_successors(self):
        return self.successors

def topological_sort(jobs, successors):
    in_degree = defaultdict(int)
    sorted_order = []

    # Calculate in-degree for each job
    for job in jobs:
        for successor in successors[job]:
            in_degree[successor] += 1

    # Find jobs with no incoming edges (in-degree = 0)
    sources = [job for job in jobs if job not in in_degree or in_degree[job] == 0]
    sources_to_return = [job for job in jobs if job not in in_degree or in_degree[job] == 0]
    sinks = []

    # Perform topological sort
    while sources:
        job = sources.pop(0)
        sorted_order.append(job)

        # Decrement the in-degree of each successor and add to sources if in-degree becomes 0
        for successor in successors[job]:
            in_degree[successor] -= 1
            if in_degree[successor] == 0:
                sources.append(successor)

        # Check if the job is a sink (no outgoing edges)
        if job not in successors or len(successors[job]) == 0:
            sinks.append(job)

    return sources_to_return, sinks, sorted_order

def calculate_earliest_times(network):
    jobs = network.get_jobs()
    predecessors = network.get_predecessors()

    earliest_start_time = {}
    earliest_finish_time = {}

    # Calculate earliest start and finish times
    for job in network.sources:
        earliest_start_time[job] = 0  # Initialize earliest start time to 0

    for job in jobs:
        if job not in predecessors or len(predecessors[job]) == 0:
            # Job has no dependencies, set earliest finish time to its duration
            earliest_finish_time[job] = job.duration
        else:
            # Calculate earliest finish time as the maximum of earliest finish times of dependent jobs
            earliest_start_time[job] = max(earliest_finish_time[predecessor] for predecessor in predecessors[job])
            earliest_finish_time[job] = earliest_start_time[job] + job.duration

    return earliest_start_time, earliest_finish_time


def calculate_latest_times(network, earliest_finish_time):
    jobs = network.get_jobs()
    successors = network.get_successors()

    latest_start_time = {}
    latest_finish_time = {}

    project_duration = max(earliest_finish_time.values())

    # Calculate latest start and finish times
    for job in network.sinks:
        latest_finish_time[job] = project_duration  # Initialize latest finish time to project duration
        latest_start_time[job] = project_duration - job.duration

    jobs.reverse()
    for job in jobs:
        # Calculate latest start time as the minimum of latest start times of dependent jobs
        if job in network.sinks:
            continue
        else:
            latest_finish_time[job] = min(latest_start_time[successor] for successor in successors[job])
            latest_start_time[job] = latest_finish_time[job] - job.duration
    
    return dict(reversed(list(latest_start_time.items()))),  dict(reversed(list(latest_finish_time.items())))


def calculate_slacks(earliest_start_time, latest_start_time):
    slacks = {}
    for job in earliest_start_time:
        slack_time = latest_start_time[job] - earliest_start_time[job]
        slacks[job] = slack_time
    return slacks


def calculate_critical_path(slacks):
    critical_path = [job for job, slack_time in slacks.items() if slack_time == 0]
    return critical_path


def cpm_algorithm(network):
    earliest_start_time, earliest_finish_time = calculate_earliest_times(network)
    latest_start_time, latest_finish_time = calculate_latest_times(network, earliest_finish_time)
    slacks = calculate_slacks(earliest_start_time, latest_start_time)
    critical_path = calculate_critical_path(slacks)
    return earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path


def main():
    jobs = {1: Job('1', 4, predecessors=[]), 
            2: Job('2', 6, predecessors=[]), 
            3: Job('3', 10, predecessors=[]), 
            4: Job('4', 12, predecessors=[1]), 
            5: Job('5', 10, predecessors=[2]), 
            6: Job('6', 2, predecessors=[3, 4, 5]), 
            7: Job('7', 4, predecessors=[3, 4]), 
            8: Job('8', 2, predecessors=[6, 7])}
 
    # Create the network and add jobs and dependencies
    network = Network(jobs)

    # Run the CPM algorithm
    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path = cpm_algorithm(
        network
    )

    # Print the results
    print("Earliest Start Time:", earliest_start_time)
    print("Earliest Finish Time:", earliest_finish_time)
    print("Latest Start Time:", latest_start_time)
    print("Latest Finish Time:", latest_finish_time)
    print("Slacks:", slacks)
    print("Critical Path:", critical_path)
    print("Makespan: ", max(earliest_finish_time.values()))


if __name__ == "__main__":
    main()
