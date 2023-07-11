import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from CPM import *

# Define a class State to represent each state with its incoming and outgoing jobs
class State(object):
    def __init__(self, id) -> None:
        self.id = id
        self.incoming = []
        self.outgoing = []

    def add_incoming(self, job_id) -> None:
        self.incoming.append(job_id)

    def add_outgoing(self, job_id) -> None:
        self.outgoing.append(job_id)

    def subset(self, state) -> bool:
        pass

    def __str__(self) -> str:
        return f"State {self.id}"
    
    def __repr__(self) -> str:
        return f"State {self.id}" # : Incoming jobs = {self.incoming}, Outgoing jobs = {self.outgoing}

    
class States(object):
    def __init__(self, states) -> None:
        self.states = states
        self.shared_outgoing = self.find_shared_outgoing()
        for key in self.shared_outgoing.keys():
            states = self.shared_outgoing[key]
            state = states[0]
            for i in range(1, len(states)):
                state.add_incoming(states[i].incoming[0])
                for k, v in self.states.items():
                    if self.states[k] == states[i]:
                        self.states[k] = state
        print(self.states)
        
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
        print(shared_outgoing)
        return shared_outgoing


def visualize_CPM() -> None:
    # Create the network and add jobs and dependencies
    jobs = {1: Job('1', 4, predecessors=[]), 
            2: Job('2', 6, predecessors=[]), 
            3: Job('3', 10, predecessors=[]), 
            4: Job('4', 12, predecessors=[1]), 
            5: Job('5', 10, predecessors=[2]), 
            6: Job('6', 2, predecessors=[3, 4, 5]), 
            7: Job('7', 4, predecessors=[3, 4]), 
            8: Job('8', 2, predecessors=[6, 7])}
    
    network = Network(jobs)

    # Run the CPM algorithm
    earliest_start_time, earliest_finish_time, latest_start_time, latest_finish_time, slacks, critical_path = cpm_algorithm(network)

    # Create a dictionary to store all states
    states = {0: State(0)}

    # Add jobs with no predecessors starting from "state 0"
    for job in network.sources:
        states[0].add_outgoing(job.id)

    # Add the rest of the jobs
    for job in jobs.values():
        states[job] = State(job.id)
        states[job].add_incoming(job)
    for job in jobs.values():
        for predecessor_id in job.predecessors:
            states[jobs[predecessor_id]].add_outgoing(job)

    st = States(states)
    states = st.states_dict()

    # Create a directed graph
    G_jobs_states = nx.DiGraph()

    for state in states.values():
        print(state.id, state.incoming, state.outgoing)
    print(states)
    # Add edges based on the states
    for state in states.values():
        for outgoing in state.outgoing:
            G_jobs_states.add_edge(state, states[jobs[int(str(outgoing))]], label="job " + str(outgoing))

    # Draw the graph
    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G_jobs_states, seed=7)  # positions for all nodes - seed for reproducibility
    nx.draw(G_jobs_states, pos, with_labels=True, node_color='skyblue', node_size=2000, width=2.0, alpha=0.6, edge_color='gray')
    nx.draw_networkx_edge_labels(G_jobs_states, pos, edge_labels=nx.get_edge_attributes(G_jobs_states, 'label'), label_pos=0.5)
    plt.title('Workflow as a Directed Acyclic Graph (States and Jobs on Edges)')
    plt.savefig('CPM.png')
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