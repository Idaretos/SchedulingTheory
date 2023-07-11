import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from CPM import *

class Node(object):
    def __init__(self, incoming_edges, outgoing_edges) -> None:
        self.incoming_edges = [incoming_edges]
        self.outgoing_edges = outgoing_edges
    
    def add_outgoing_edge(self, edge):
        self.outgoing_edges.append(edge)

def visualize_CPM():
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

    # Create a directed graph
    graph = nx.DiGraph()

    # # find predecessor count
    # job_count = len(jobs)
    # predecessor_count = 0
    # for job in jobs.values():
    #     predecessor_count += len(job.predecessors)

    # # Add nodes representing jobs and display earliest time and latest time as labels
    # for job in jobs.values():
    #     graph.add_node(job, label=f'{earliest_start_time[job]}/{latest_start_time[job]}')

    # # Add nodes representing predecessors and find out the incoming and outgoing edges
    # for i in range(predecessor_count):
    #     graph.add_node(i, label=f'{earliest_start_time[job]}/{latest_start_time[job]}')

    # Find out the incoming and outgoing edges for each nodes and create nodes

    # Starting node
    graph.add_node('start', label=f'0 / {min(latest_start_time[source] for source in network.sources)}')
    predecessors = defaultdict(list)
    successors = defaultdict(list)
    for id, job in jobs.items():
        for predecessor_id in job.predecessors:
            predecessors[id].append(predecessor_id)
            if jobs[id] not in successors[predecessor_id]:
                successors[predecessor_id].append(id)

    out_in = defaultdict(list)
    for job in jobs.values():
        for predecessor_id in job.predecessors:
            out_in[tuple(successors[predecessor_id])].append(predecessor_id)
        
    print(list(out_in.keys()))
    out_dict = find_subsets(list(out_in.keys()))
    print(out_dict)
    for key, value in out_dict.items():
        print(key, value)
    
    # for source in network.sources:
    #     edge_name = source.id
    #     graph.add_node('next', label=f'{latest_finish_time[source]} / ')
    #     graph.add_edge(source, source.id, label=edge_name)
        

    # Add arcs representing dependencies with weights shown within edge names
    for job in jobs.values():
        for predecessor in job.predecessors:
            edge_name = f'{jobs[predecessor].duration} ({predecessor}->{job.id})'
            graph.add_edge(predecessor, job.id, label=edge_name)

    # Define the critical path
    critical_path_nodes = [job.id for job in critical_path]

    # Draw the graph
    pos = nx.spring_layout(graph)  # Set the layout of the graph

    # Draw non-critical edges
    non_critical_edges = [(u, v) for u, v in graph.edges() if u not in critical_path_nodes or v not in critical_path_nodes]
    nx.draw_networkx_edges(graph, pos, edgelist=non_critical_edges, edge_color='gray', arrows=True)

    # Draw critical edges
    critical_edges = [(u, v) for u, v in graph.edges() if u in critical_path_nodes and v in critical_path_nodes]
    nx.draw_networkx_edges(graph, pos, edgelist=critical_edges, edge_color='red', arrows=True)

    # Draw edge labels within the edge names
    edge_labels = nx.get_edge_attributes(graph, 'label')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=8)

    # Draw non-critical nodes
    non_critical_nodes = [node for node in graph.nodes() if node not in critical_path_nodes]
    nx.draw_networkx_nodes(graph, pos, nodelist=non_critical_nodes, node_color='lightblue', node_size=500)

    # Draw critical nodes
    nx.draw_networkx_nodes(graph, pos, nodelist=critical_path_nodes, node_color='red', node_size=500)

    # Draw node labels (earliest time and latest time)
    node_labels = nx.get_node_attributes(graph, 'label')
    nx.draw_networkx_labels(graph, pos, labels=node_labels, font_size=10)

    # Show the plot
    plt.axis('off')
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