import pygraphviz as pgv
import networkx as nx
import matplotlib.pyplot as plt
import os
from networkx.drawing.nx_agraph import graphviz_layout
from collections import defaultdict
from CPM import *

# Define a class State to represent each state with its incoming and outgoing jobs
class State(object):
    def __init__(self, id, is_critical=False) -> None:
        self.id = id
        self.is_critical = is_critical
        self.incoming = []
        self.outgoing = []

    def add_incoming(self, job_id) -> None:
        self.incoming.append(job_id)

    def add_outgoing(self, job_id) -> None:
        self.outgoing.append(job_id)

    def subset(self, state) -> bool:
        tmpset =  set(self.outgoing) - set(state.outgoing)
        if tmpset != set(self.outgoing) and tmpset != set([]):
            return True
        return False

    def __str__(self) -> str:
        return f"State {self.id}"
    
    def __repr__(self) -> str:
        return f"State {self.id}" # : Incoming jobs = {self.incoming}, Outgoing jobs = {self.outgoing}
    
    def __eq__(self, other) -> bool:
        if isinstance(other, State):
            return (self.id == other.id and self.outgoing == other.outgoing)
        return False
    
    def __hash__(self) -> int:
        return int(self.id)

    
class States(object):
    def __init__(self, states) -> None:
        self.states = states
        self.shared_outgoing = self.find_shared_outgoing()
        self.dummies = []
        for key in self.shared_outgoing.keys():
            states = self.shared_outgoing[key]
            state = states[0]
            for st in states:
                if st.is_critical:
                    state = st
            for i in range(0, len(states)):
                if states[i] != state:
                    state.add_incoming(states[i].incoming[0])
                for k, v in self.states.items():
                    if self.states[k] == states[i]:
                        self.states[k] = state
            for dummy_state in self.states.values():
                if state.subset(dummy_state):
                    dummy = Job(f'{dummy_state.id}', 0, [], is_dummy=True)
                    state.add_outgoing(dummy)
                    self.dummies.append(dummy)
        
    def states_dict(self):
        return self.states

    def find_shared_outgoing(self) -> dict:
        # Create a dictionary where the keys are the outgoing jobs, and the values are lists of states
        outgoing_dict = defaultdict(list)
        for state in self.states.values():
            # Convert the list of outgoing jobs to a tuple so it can be used as a dictionary key
            outgoing_tuple = tuple(sorted(state.outgoing))
            outgoing_dict[outgoing_tuple].append(state)

        # Find and return only those outgoing jobs that are shared by more than one state
        shared_outgoing = {outgoing: states for outgoing, states in outgoing_dict.items() if len(states) > 1}
        return shared_outgoing


def visualize_CPM(jobs, critical_path, outputpath='SchedulingTheory/CPM/output') -> None:    
    network = Network(jobs)

    # Create a dictionary to store all states
    states = {0: State(0, is_critical=True)}

    # Add jobs with no predecessors starting from "state 0"
    for job in network.sources:
        states[0].add_outgoing(job)

    # Add the rest of the jobs
    for job in jobs.values():
        is_critical = False
        if job in critical_path:
            is_critical = True
        states[job] = State(job.id, is_critical)
        states[job].add_incoming(job)
    for job in jobs.values():
        for predecessor_id in job.predecessors:
            states[jobs[predecessor_id]].add_outgoing(job)

    st = States(states)
    states = st.states

    # Create a directed graph
    graph = nx.DiGraph()

    # Add edges based on the states
    for state in states.values():
        if state.id == '3':
            print()
        for outgoing in state.outgoing:
            if not outgoing.is_dummy:
                graph.add_edge(state, states[jobs[int(outgoing.id)]], label="job " + str(outgoing), is_critical=(outgoing in critical_path), is_dummy=False)
            else:
                graph.add_edge(state, states[jobs[int(outgoing.id)]], label='dummy', is_critical=(state.is_critical and states[jobs[int(outgoing.id)]].is_critical), is_dummy=True)

    # Draw the graph
    plt.figure(figsize=(8, 6))
    # pos = nx.spring_layout(graph, seed=3)  # positions for all nodes - seed for reproducibility
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
    critical_path_nodes = [node for node in graph.nodes() if node.is_critical]
    nx.draw_networkx_nodes(graph, pos, nodelist=critical_path_nodes, node_color='red', node_size=500)

    # Draw node labels (earliest time and latest time)
    node_labels = nx.get_node_attributes(graph, 'label')
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=10)


    # nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=2000, width=2.0, alpha=0.6, edge_color='gray')
    # nx.draw_networkx_edge_labels(graph, pos, edge_labels=nx.get_edge_attributes(graph, 'label'), label_pos=0.5)
    plt.title('Critical Path Method')
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    plt.savefig(outputpath+'/CPM.png')
    plt.show()


def find_subsets(superlist):
    results = {}
    for i, A in enumerate(superlist):
        for j, B in enumerate(superlist):
            if i != j and set(A).issubset(B):
                results[A] = B
    return results

if __name__ == '__main__':
    visualize_CPM()