from typing import Tuple, List, Dict
from itertools import chain, combinations
from Jobs import *
from AdjacencyTable import AdjacencyTable
from CPM_visualize import *
from matplotlib.widgets import Button
import matplotlib.pyplot as plt
import warnings
import pulp
import time


class PathFinder(object):
    def __init__(self, workflow, costs) -> None:
        self.workflow = workflow
        self.costs = costs
        self.jobs = self.create_jobs(workflow, costs)
        self.network: Network = Network(self.jobs)
        self.graph = AdjacencyTable()
        self.paths = self.all_paths()
        self.makespan = -1
        self.critical_paths = []
        self.save_dict = {}
        for job1 in self.network.jobs:
            for job2 in job1.predecessors:
                self.graph.add_edge(job2, job1.id)

    def __repr__(self) -> str:
        return 'PathFinder'
    
    @staticmethod
    def create_jobs(workflow, costs) -> Dict[str, Job]:
        workflow['predecessors'] = workflow['predecessors']
        ids = workflow['id'].tolist()
        predecessors = workflow['predecessors'].tolist()
        p_maxs = costs['p_max'].tolist()
        p_mins = costs['p_min'].tolist()
        min_costs = costs['min_cost'].tolist()
        marginal_costs = costs['marginal_cost'].tolist()
        jobs = {}
        for i in range(len(ids)):
            jobs[str(ids[i])] = Job(str(ids[i]), predecessors[i], p_maxs[i], p_mins[i], min_costs[i], marginal_costs[i])
        return jobs
    
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
        # self.save_dict = {}
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
        key = (tuple(subset), tuple(default_constraint))
        if key in self.save_dict:
            return self.save_dict[key]
        
        subset = [job.id for job in subset]
        constraint = set(subset) | default_constraint
        for source in self.network.sources:
            for sink in self.network.sinks:
                if self.graph.is_reachable(source.id, sink.id, constraint):
                    self.save_dict[key] = False
                    return False
        self.save_dict[key] = True
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
    def __init__(self, workflow, costs, c0):
        super().__init__(workflow, costs)
        self.rule = 'heuristic'
        self.c0 = c0  # Fixed overhead cost per unit time
        self.linear_output=None
        self.start_time = None

    def __rerp__(self) -> str:
        return 'Optimizer'

    def optimize(self, rule='heuristic',visualize=False) -> None:
        '''
        optimize time/cost trade-offs by certain rule
        '''
        # Start time recording
        start_time = time.time()
        self.start_time = start_time
        self.rule = rule
        if rule == 'heuristic':
            print("Processing...")
            self.linear_output = None
            self.heuristic(visualize)
        elif rule == 'linear' or rule == 'lp':
            self.rule = 'linear'
            if visualize:
                warnings.warn('linear optimization does not support visualization')
            self.linear()

    def heuristic(self, visualize=False) -> None:
        # Step 1.
        # Set all processing times at their maximum.
        for job in self.network.jobs:
            job.duration = job.p_max

        step = 0

        # Determine all critical path(s) with these processing times.
        critical_path, makespan = self.CPM()
        if visualize:
            visualize_CPM(self.jobs, (critical_path, makespan), self.paths, title=f'Initial.')
        
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
                    visualize_CPM(self.jobs, (critical_path, makespan), self.paths, emphasize=[job.id for job in min_cost_cut_set], title=f'step {step}.')
            else:
                break
        if visualize:
            visualize_CPM(self.jobs, (critical_path, makespan), self.paths, title='Final.')

        for path in self.paths:
            tmp_span = 0
            for job in path:
                tmp_span += job.duration
            if tmp_span == makespan:
                self.critical_paths.append(path)

        self.makespan = makespan
        if visualize:
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.subplots_adjust(bottom=0.2)
            class Index:
                current_index = 0
                @staticmethod
                def draw_graph(data, ax):
                    ax.clear()
                    nx.draw(data['graph'], pos=data['positions'], with_labels=False, ax=ax)
                    # Draw edge labels
                    nx.draw_networkx_edge_labels(data['graph'], pos=data['positions'], edge_labels=data['edge_labels'], ax=ax)
                    # Draw emphasized edges
                    nx.draw_networkx_edges(data['graph'], pos=data['positions'], edgelist=data['emphasize_edges'], edge_color='blue', ax=ax)
                    # Draw non-critical, non-dummy edges
                    nx.draw_networkx_edges(data['graph'], pos=data['positions'], edgelist=data['non_critical_non_dummy_edges'], edge_color='black', ax=ax)
                    # Draw non-critical dummy edges
                    nx.draw_networkx_edges(data['graph'], pos=data['positions'], edgelist=data['non_critical_dummy_edges'], edge_color='lightgray', ax=ax)
                    # Draw critical edges
                    nx.draw_networkx_edges(data['graph'], pos=data['positions'], edgelist=data['critical_edges'], edge_color='red', ax=ax)
                    # Draw critical, emphasized edges
                    nx.draw_networkx_edges(data['graph'], pos=data['positions'], edgelist=data['emp_critical_edges'], edge_color='darkblue', width=3, ax=ax)
                    # Draw non-critical nodes
                    nx.draw_networkx_nodes(data['graph'], pos=data['positions'], nodelist=data['non_critical_nodes'], node_color='lightblue', ax=ax)
                    # Draw critical nodes
                    nx.draw_networkx_nodes(data['graph'], pos=data['positions'], nodelist=data['critical_path_nodes'], node_color='red', ax=ax)
                    # Draw starting, ending nodes
                    nx.draw_networkx_nodes(data['graph'], pos=data['positions'], nodelist=data['polar_nodes'], node_color='darkblue', ax=ax)
                    # Set title
                    plt.title(data['title'])
                    # Add legend
                    ax.legend(handles=[data['makespan_line'], data['c_line'], data['j_line'], data['d_line']], loc='lower left', frameon=False)
                    plt.draw()

                def next(self, event):
                    data = PLOTS[self.current_index]
                    self.current_index = min(self.current_index + 1, len(PLOTS)-1)
                    self.draw_graph(data, ax)
                def prev(self, event):
                    self.current_index = max(self.current_index -1, 0)
                    data = PLOTS[self.current_index]
                    self.draw_graph(data, ax)

            callback = Index()
            axprev = fig.add_axes([0.7, 0.05, 0.1, 0.075])
            axnext = fig.add_axes([0.81, 0.05, 0.1, 0.075])
            bnext = Button(axnext, 'Next')
            bnext.on_clicked(callback.next)
            bprev = Button(axprev, 'Previous')
            bprev.on_clicked(callback.prev)
            callback.next(None)
            print("\033[A                             \033[A")
            duration = time.time() - self.start_time
            print(f"Took {duration:.2f} seconds")
            self.show()
            plt.show()
        else:
            print("\033[A                             \033[A")
            duration = time.time() - self.start_time
            print(f"Took {duration:.2f} seconds")
            self.show()

    # The optimize function will now perform the optimization and return the final critical path after all possible reductions.

    def linear(self):
        def create_lp_jobs(workflow, costs) -> tuple:
            workflow['predecessors'] = workflow['predecessors']
            predecessors = workflow['predecessors'].tolist()
            p_maxs = costs['p_max'].tolist()
            p_mins = costs['p_min'].tolist()
            min_costs = costs['min_cost'].tolist()
            marginal_costs = costs['marginal_cost'].tolist()
            n = len(marginal_costs)
            
            return n, predecessors, p_maxs, p_mins, min_costs, marginal_costs

        def cal_costs(n, min_costs, p_mins, marginal_costs, p):
            costs = []
            for i in range(n):
                costs.append(min_costs[i] + marginal_costs[i]*(p[i]-p_mins[i]))
            return costs
        
        n, predecessors, p_max, p_min, min_costs, c = create_lp_jobs(self.workflow, self.costs)

        # Create a linear programming problem
        lp_problem = pulp.LpProblem("Job_Scheduling", pulp.LpMinimize)

        # Decision variables
        p = pulp.LpVariable.dicts("p", range(1, n+1), lowBound=0)
        x = pulp.LpVariable.dicts("x", range(1, n+1), lowBound=0)
        C_max = pulp.LpVariable("C_max", lowBound=0)

        # Objective function
        lp_problem += self.c0*C_max - pulp.lpSum([c[j-1]*p[j] for j in range(1, n+1)])

        # Constraints
        # Precedence constraints
        for j in range(n):
            if predecessors[j]:
                for pred in predecessors[j]:
                    lp_problem += x[j+1] - p[pred] - x[pred] >= 0

        # p_min and p_max constraints
        for j in range(n):
            lp_problem += p[j+1] >= p_min[j]
            lp_problem += p[j+1] <= p_max[j]

        # C_max constraints
        for j in range(n):
            lp_problem += x[j+1] + p[j+1] <= C_max

        # Solve the problem
        lp_problem.solve()

        # Extract results
        results_p = [p[j].varValue for j in range(1, n+1)]
        results_x = [x[j].varValue for j in range(1, n+1)]
        results_C_max = C_max.varValue

        results_costs = cal_costs(n, min_costs, p_min, c, results_p)
        self.linear_output = (results_x, results_p, results_costs, results_C_max)
        duration = time.time() - self.start_time
        print(f"Took {duration:.2f} seconds\n")
        self.show()
        

    def show(self):
        if self.rule == 'heuristic':
            print_jobs(list(self.jobs.values()))
            print('critical_paths:')
            for path in self.critical_paths:
                print(end='  ')
                print_path(path)
            print(f'Costs:\t\t{total_cost(list(self.jobs.values()))}')
            print(f'makespan:\t{self.makespan}')
        elif self.rule == 'linear':
            results_x, results_p, results_costs, results_C_max = self.linear_output
            print("Start times:\t\t", results_x)
            print("Processing times:\t", results_p)
            print("Costs:\t\t\t", results_costs)
            print("Makespan:\t\t", results_C_max)
        self.start_time = None
