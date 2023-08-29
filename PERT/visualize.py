import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os, sys, ast
from networkx.drawing.nx_agraph import graphviz_layout
from os.path import realpath, dirname
from collections import defaultdict
from CPM import *
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm
from job_PERT import *

# Define a class State to represent each state with its incoming and outgoing jobs
class State(object):
    def __init__(self, id, is_critical=False) -> None:
        self.id = id
        self.is_critical = is_critical
        self.incoming = []
        self.outgoing = []

    def add_incoming(self, job) -> None:
        self.incoming.append(job)

    def add_outgoing(self, job) -> None:
        self.outgoing.append(job)                

    def subset(self, state) -> bool:
        tmpset =  set(self.outgoing) - set(state.outgoing)
        if tmpset != set(self.outgoing) and tmpset != set([]):
            return True
        return False
    
    def outgoing_equals(self, other) -> bool:
        if isinstance(other, State):
            return (self.id == other.id and self.outgoing == other.outgoing)
        return False

    def incoming_equals(self, other) -> bool:
        if isinstance(other, State):
            return self.outgoing == other.outgoing
        return False

    def __str__(self) -> str:
        return f"State {self.id}"
    
    def __repr__(self) -> str:
        return f"State {self.id}"
    
    def __eq__(self, other) -> bool:
        if isinstance(other, State):
            return (self.id == other.id
                    and self.is_critical == other.is_critical
                    and self.incoming == other.incoming
                    and self.outgoing == other.outgoing)
        return False
    
    def __hash__(self) -> int:
        return int(self.id)

    
class StateAssembler(object):
    def __init__(self, states) -> None:
        self.__states = states

    def run(self, jobs, critical_path) -> None:
        shared_outgoing = self.__find_shared_outgoing()

        # Find states that have exact same outgoing and incoming jobs, and connect them with dummies
        for states in shared_outgoing:
            shared_predecessor = self.__find_shared_predecessor(states, jobs)
            if len(shared_predecessor) > 0:
                for shared_states in shared_predecessor:
                    state = shared_states[0]
                    for st in shared_states:
                        if st.is_critical:
                            state = st
                            break
                    for st in shared_states:
                        if st != state:
                            dummy = Job(f'{state.id}', 0, [], is_dummy=True, prev_state=st)
                            st.outgoing = [dummy]
                            state.add_incoming(dummy)

        # Exclude the states that has gotten dummy outgoing job
        shared_outgoing = self.__find_shared_outgoing()

        # Find states that have exact same outgoing jobs, and merge them
        for states in shared_outgoing:
            state = states[0]
            for st in states:
                if st.is_critical:
                    state = st
                    break
            for i in range(0, len(states)):
                if states[i] != state:
                    state.add_incoming(states[i].incoming[0])
                for k, v in self.__states.items():
                    if self.__states[k].outgoing_equals(states[i]):
                        self.__states[k] = state
                        
        # Find states that share outgoing jobs and connect them with dummies
        for state in self.__states.values():
            for dummy_state in self.__states.values():
                if state.subset(dummy_state):
                    if dummy_state.outgoing[0].is_dummy:
                        continue
                    state.outgoing = list(set(state.outgoing) - set(dummy_state.outgoing))
                    dummy = Job(f'{dummy_state.id}', 0, [], is_dummy=True, prev_state=state)
                    if len([x for x in state.incoming if x in critical_path])*len([x for x in dummy_state.outgoing if x in critical_path]) > 0:
                        critical_path.append(dummy)
                        dummy_state.is_critical = True
                    state.add_outgoing(dummy)
                    dummy_state.add_incoming(dummy)

    def __call__(self, jobs, critical_path):
        self.run(jobs, critical_path)
        return self.__states
    
    # Find states that have exact same predecessors
    @staticmethod
    def __find_shared_predecessor(states, jobs) -> dict:
        incoming_dict = defaultdict(list)
        for state in states:
            predecessor_tuple = tuple(sorted(jobs[state.id].predecessors))
            incoming_dict[predecessor_tuple].append(state)

        shared_predecessor = [states for predecessor, states in incoming_dict.items() if len(states) > 1]
        return shared_predecessor

    # Find states that have exact same outgoing jobs
    def __find_shared_outgoing(self) -> dict:
        # Create a dictionary where the keys are the outgoing jobs, and the values are lists of states
        outgoing_dict = defaultdict(list)
        for state in self.__states.values():
            # Convert the list of outgoing jobs to a tuple so it can be used as a dictionary key
            outgoing_tuple = tuple(sorted(state.outgoing))
            outgoing_dict[outgoing_tuple].append(state)

        # Find and return only those outgoing jobs that are shared by more than one state
        shared_outgoing = [states for outgoing, states in outgoing_dict.items() if len(states) > 1]
        return shared_outgoing


def all_paths(network) -> list:
        def dfs(current, path):
            # If the current job is a sink, add the path to the result
            if current in network.sinks:
                paths.append(path)
                return
            
            # Explore the successors of the current job
            for successor in network.successors[current.id]:
                dfs(successor, path + [successor])

        paths = []
        # Start DFS from each source in the network
        for source in network.sources:
            dfs(source, [source])

        return paths

DEAFULT_PATH = os.path.dirname(os.path.realpath(__file__))+'/output'
def visualize_PERT(jobs: dict, CPM_results: tuple, network: Network, outputpath: str=DEAFULT_PATH) -> None:
    mode_path_proportion, a, a, a, a, critical_path, makespan = CPM_results
    critical_paths = network.critical_paths

    # Create a dictionary to store all states
    states = {'0': State('0', is_critical=True)}

    # Add jobs with no predecessors starting from "state 0"
    for job in network.sources:
        states['0'].add_outgoing(job)

    # Add the rest of the jobs
    for job in jobs.values():
        is_critical = False
        if job in critical_path:
            is_critical = True
        states[job.id] = State(job.id, is_critical)
        states[job.id].add_incoming(job)
    for job in jobs.values():
        for predecessor_id in job.predecessors:
            states[predecessor_id].add_outgoing(job)

    state_assembler = StateAssembler(states)
    states = state_assembler(jobs, critical_path)

    # Create a directed graph
    graph = nx.DiGraph()

    graph.graph['graph'] = {'rankdir': 'LR'}

    # Add edges based on the states
    for state in states.values():
        for outgoing in state.outgoing:
            if not outgoing.is_dummy:
                graph.add_edge(state, states[outgoing.id], label=f"J{str(outgoing)}", is_critical=(outgoing in critical_path), is_dummy=False)
            else:
                truth = [False, False]
                out_state = states[outgoing.id]
                for path in critical_paths:
                    truth = [False, False]
                    for incoming in state.incoming:
                        if incoming in path:
                            truth[0] = True
                    for outgoing in out_state.outgoing:
                        if outgoing in path:
                            truth[1] = True
                    if truth[0] and truth[1]:
                        break
                graph.add_edge(state, out_state, label='D', is_critical=(truth[0] and truth[1]), is_dummy=True)
    # Draw the graph
    plt.figure(figsize=(12, 6))
    pos = graphviz_layout(graph, prog='dot')

    # Draw edge labels within the edge names
    edge_labels = nx.get_edge_attributes(graph, 'label')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)

    # Draw non-critical, non-dummy edges
    non_critical_non_dummy_edges = [(u, v) for u, v, d in graph.edges(data=True) if not d['is_critical'] and not d['is_dummy']]
    nx.draw_networkx_edges(graph, pos, edgelist=non_critical_non_dummy_edges, edge_color='black', arrows=True)

    # Draw non-critical dummy edges
    non_critical_dummy_edges = [(u, v) for u, v, d in graph.edges(data=True) if not d['is_critical'] and d['is_dummy']]
    nx.draw_networkx_edges(graph, pos, edgelist=non_critical_dummy_edges, edge_color='lightgray', arrows=True)

    # Draw critical edges
    critical_edges = [(u, v) for u, v, d in graph.edges(data=True) if d['is_critical']]
    nx.draw_networkx_edges(graph, pos, edgelist=critical_edges, edge_color='red', arrows=True)

    # Draw non-critical nodes
    non_critical_nodes = [node for node in graph.nodes() if not node.is_critical]
    nx.draw_networkx_nodes(graph, pos, nodelist=non_critical_nodes, node_color='lightblue', node_size=500)

    # Draw critical nodes
    critical_path_nodes = [node for node in graph.nodes() if node.is_critical and not (len(node.incoming) == 0 or len(node.outgoing) == 0)]
    nx.draw_networkx_nodes(graph, pos, nodelist=critical_path_nodes, node_color='red', node_size=500)

    # Draw starting, ending nodes
    polar_nodes = [node for node in graph.nodes() if (len(node.incoming) == 0 or len(node.outgoing) == 0)]
    nx.draw_networkx_nodes(graph, pos, nodelist=polar_nodes, node_color='darkblue', node_size=500)

    plt.title('PERT')
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    makespan_line = mlines.Line2D([], [], color='none', label=f'Mode Makespan: {makespan}')
    mode_path_proportion_line = mlines.Line2D([], [], color='none', label=f'Proportion = {mode_path_proportion}%')
    c_line = mlines.Line2D([], [], color='red', marker='_', markersize=15, label='Mode Critical Paths')
    j_line = mlines.Line2D([], [], color='black', marker='_', markersize=15, label='Jn: Job n')
    d_line = mlines.Line2D([], [], color='lightgray', marker='_', markersize=15, label='D: Dummy Job')

    # Add the legend to the plot
    plt.legend(handles=[makespan_line, mode_path_proportion_line, c_line, j_line, d_line], loc='lower left', frameon=False)

    plt.savefig(outputpath+'/PERT.png')
    plt.show()

def run(inputpath, outputpath, threshold):
    df = pd.read_csv(inputpath)

    # Convert the "predecessors" column to a list
    df['predecessors'] = df['predecessors'].apply(ast.literal_eval)
    df['id'] = df['id'].apply(str)


    # Convert the DataFrame to a dictionary
    jobs_dict = df.to_dict('index')

    # Convert the keys to 'id'
    jobs_dict = {value['id']: value for key, value in jobs_dict.items()}

    jobs = {id: OJob(**job_data) for id, job_data in jobs_dict.items()}

    # Create the network and add jobs and dependencies
    network = Network(jobs)

    # Find out all possible paths
    paths = all_paths(network)

    # Run the CPM algorithm
    CPM_results = CPM(network)
    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan = CPM_results
    mean = 0
    std = 0
    for critical_path in network.critical_paths:
        id_list = [job.id for job in critical_path]
        X = df[df['id'].isin(id_list)]
        X = X[['optimistic', 'most_likely', 'pessimistic']].values
        
        tmp_mean = 0
        tmp_std = 0
        for i in range(len(X)):
            tmp_mean += (X[i][0]+4*X[i][1]+X[i][2])/6
            tmp_std += ((X[i][2]-X[i][0])/6)*((X[i][2]-X[i][0])/6)
        tmp_std = np.sqrt(tmp_std)

        if tmp_mean > mean:
            mean = tmp_mean
            std = tmp_std

    makespans = []
    critical_paths = defaultdict(int)
    tmp = {}
    tmp_makespans = defaultdict(list)

    ITERATION = 50000
    for i in range(ITERATION):
        jobs, CPM_results, network = cal(jobs_dict)
        earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan = CPM_results
        makespans += [makespan]
        for critical_path in network.critical_paths:
            critical_paths[str(critical_path)] += 1
            tmp[str(critical_path)] = (jobs, CPM_results, network)
            tmp_makespans[str(critical_path)].append(makespan)

    plt.figure()
    min_makespan = np.min(makespans)
    max_makespan = np.max(makespans)
    sns.kdeplot(makespans, fill=True)
    x = np.linspace(min_makespan, max_makespan, 1000)
    y = (1 / np.sqrt(2 * np.pi * std**2)) * np.exp(-(x-mean)**2 / (2 * std**2))
    plt.plot(x, y)
    if threshold is not None:
        plt.axvline(x=threshold, color='blue', linestyle='--', label=f'{threshold}')
    plt.title('Density Plot of Makespans')
    plt.xlabel('Makespan')
    plt.savefig(outputpath+'/density_plot.png')
    
    max_key = max(critical_paths, key=critical_paths.get)
    jobs, CPM_results, network = tmp[max_key]

    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path, makespan = CPM_results
    CPM_results = earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, list(max_key), makespan
    makespan = round(np.average(tmp_makespans[max_key]), 1)
    mode_path_proportion = np.round(critical_paths[max_key]/ITERATION*100, 2)
    print("Mode Critical Path:", max_key)
    print("Mode Makespan: ", makespan)
    print(f"Mode Path Proportion:  {mode_path_proportion}%")
    if threshold is not None:
        print(f'             \tsim\texpected')
        print(f'Prob over {threshold}:\t{round(100.0*sum(1 for span in makespans if span > threshold)/len(makespans), 2)}%\t{round(100.0*(1-norm.cdf(threshold, mean, std)), 2)}%')

    CPM_results = (mode_path_proportion, 0, 0, 0, 0, critical_path, makespan)
    visualize_PERT(jobs, CPM_results, network, outputpath=outputpath)


def cal(jobs_dict):
    # Convert the dictionary back to Job objects
    jobs = {id: PJob(**job_data) for id, job_data in jobs_dict.items()}

    # Create the network and add jobs and dependencies
    network = Network(jobs)

    # Run the CPM algorithm
    CPM_results = CPM(network)
    return jobs, CPM_results, network
