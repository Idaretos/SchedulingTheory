from typing import Any, Tuple, List, Dict
from itertools import chain, combinations
from Jobs import *
from AdjacencyTable import AdjacencyTable
from CPM_visualize import visualize_CPM

class PathFinder(object):
    def __init__(self, jobs) -> None:
        self.network: Network = Network(jobs)
        self.jobs_dict = jobs
        self.graph = AdjacencyTable()
        self.paths = self.all_paths()
        self.critical_paths = []
        for job1 in self.network.jobs:
            for job2 in job1.predecessors:
                self.graph.add_edge(job2, job1.id)

    def __repr__(self) -> str:
        return 'PathFinder'
    
    @staticmethod
    def __calculate_earliest_times(network) -> Tuple[dict, dict]:
        jobs = network.get_jobs()
        predecessors = network.predecessors

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

    @staticmethod
    def __calculate_latest_times(network, earliest_finish_time) -> Tuple[dict, dict]:
        jobs = network.get_jobs()
        successors = network.successors

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

    @staticmethod
    def __calculate_slacks(jobs, earliest_start_time, latest_start_time) -> Dict[Job, float]:
        slacks = {}
        for job in jobs:
            slack_time = latest_start_time[job.id] - earliest_start_time[job.id]
            slacks[job] = slack_time
        return slacks

    @staticmethod
    def __calculate_critical_path(slacks) -> List[Job]:
        critical_path = [job for job, slack_time in slacks.items() if slack_time == 0]
        return sorted(critical_path, key=(lambda x : int(x.id)))

    def CPM(self) -> List[Job]:
        self.network.sort()
        earliest_start_time, earliest_finish_time = self.__calculate_earliest_times(self.network)
        latest_start_time, latest_finish_time = self.__calculate_latest_times(self.network, earliest_finish_time)
        slacks = self.__calculate_slacks(self.network.jobs, earliest_start_time, latest_start_time)
        critical_path = self.__calculate_critical_path(slacks)
        makespan = max(earliest_finish_time.values())
        return critical_path, makespan

    def all_paths(self) -> List[List[Job]]:
        def dfs(current, path):
            # If the current job is a sink, add the path to the result
            if current in self.network.sinks:
                paths.append(path)
                return
            
            # Explore the successors of the current job
            for successor in self.network.successors[current.id]:
                dfs(successor, path + [successor])

        paths = []
        # Start DFS from each source in the network
        for source in self.network.sources:
            dfs(source, [source])

        return paths        

    def minimal_cut_sets(self, critical_path) -> List[List[Job]]:
        sets = []
        subsets = self.__all_subsets(critical_path)
        default_constraint = set([job.id for job in self.network.jobs])-set([job.id for job in critical_path])
        for subset in subsets:
            if self.__is_minimal_cut_set(subset, default_constraint):
                sets.append(subset)
        return sets
    
    def __is_minimal_cut_set(self, subset: List[Job], default_constraint: List[Job]) -> bool:
        if not self.__is_cut_set(subset, default_constraint):
            return False
        subsubsets = self.__all_subsets(subset)
        for subsubset in subsubsets:
            if self.__is_cut_set(subsubset, default_constraint):
                return False
        return True
        

    def __is_cut_set(self, subset: List[Job], default_constraint: List[Job]) -> bool:
        if len(subset) == 0:
            return False
        subset = [job.id for job in subset]
        constraint = set(subset) | default_constraint
        for source in self.network.sources:
            for sink in self.network.sinks:
                if self.graph.is_reachable(source.id, sink.id, constraint):
                    return False
        return True

    @staticmethod
    def __all_subsets(set) -> List[List[Job]]:
        '''
        Generate all possible subsets of a list of jobs.
        '''
        # Generate all combinations of jobs for lengths ranging from 0 to the length of the job list
        subsets = chain(*[combinations(set, i) for i in range(len(set))])
        
        return [list(subset) for subset in subsets]
    
def all_contain(item, list_of_lists):
    return all(item in sublist for sublist in list_of_lists)


class Optimizer(PathFinder):
    def __init__(self, jobs, c0):
        super().__init__(jobs)
        self.c0 = c0  # Fixed overhead cost per unit time

    def __rerp__(self) -> str:
        return 'Optimizer'

    def optimize(self, visualize=False):
        # Step 1.
        # Set all processing times at their maximum.
        for job in self.network.jobs:
            job.duration = job.p_max

        step = 0

        # Determine all critical path(s) with these processing times.
        critical_path, makespan = self.CPM()
        if visualize:
            visualize_CPM(self.jobs_dict, (critical_path, makespan), self.paths, title=f'step {step}.')
        
        while True:
            # Step 2.
            # Determine all minimum cut sets in the current critical path.
            min_cut_sets = self.minimal_cut_sets(critical_path)

            # Consider only those minimum cut sets of which all processing times are strictly larger than their minimum.
            valid_min_cut_sets = [cut_set for cut_set in min_cut_sets if all(job.duration > job.p_min for job in cut_set)]

            if not valid_min_cut_sets:
                break

            # For each minimum cut set compute the cost of reducing all its processing times by one time unit.
            costs = {}
            for cut_set in valid_min_cut_sets:
                total_cost = sum(job.marginal_cost for job in cut_set)
                costs[tuple(cut_set)] = total_cost

            # Take the minimum cut set with the lowest cost.
            min_cost_cut_set: Tuple[Job] = min(costs, key=lambda cut_set: costs[cut_set])
            
            # Step 3.
            # If this lowest cost is less than the overhead cost c0 per unit time go to Step 4, otherwise STOP.
            if costs[min_cost_cut_set] <= self.c0:
                # Step 4.
                # Reduce all the processing times in the minimum cut set by one time unit.
                for job in min_cost_cut_set:
                    job.duration -= 1

                # Determine the new set of critical paths.
                critical_path, makespan = self.CPM()
                step += 1

                if visualize:
                    print(min_cost_cut_set)
                    visualize_CPM(self.jobs_dict, (critical_path, makespan), self.paths, title=f'step {step}.')
            else:
                break
        if visualize:
            visualize_CPM(self.jobs_dict, (critical_path, makespan), self.paths, title=f'Final.')

        for path in self.paths:
            tmp_span = 0
            for job in path:
                tmp_span += job.duration
            if tmp_span == makespan:
                self.critical_paths.append(path)

        return critical_path, makespan

# The optimize function will now perform the optimization and return the final critical path after all possible reductions.
