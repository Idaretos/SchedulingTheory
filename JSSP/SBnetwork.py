import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout


class SBM(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.operations = list()

    def __repr__(self) -> str:
        return self.name


class SBJ(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.operations = list()

    def __repr__(self):
        return self.name


class SBO(object):
    def __init__(self, machine, job, duration):
        self.machine = machine
        self.job = job
        self.duration = duration
        self.id = (machine.id, job.id)
        job.operations.append(self)
        machine.operations.append(self)


class SBN(object):
    def __init__(self, jobs, machines):
        self.graph = nx.DiGraph(rankdir="LR")
        self.graph.add_node('U')
        self.graph.add_node('V')
        self.jobs = jobs
        self.machines = machines
        self.operations = dict()
        self.disjunctive_edges = set()

        for job in jobs:
            for operation in job.operations:
                self.operations[operation.id] = operation
            self.add_job(job)

        self.pos = graphviz_layout(self.graph, prog='dot')
        print(self.pos)
        
    def add_job(self, job):
        prev_node = 'U'
        w = 0
        for operation in job.operations:
            self.graph.add_node(operation.id)
            self.graph.add_edge(prev_node, operation.id, weight=w, label=w)
            prev_node = operation.id
            w = operation.duration
        self.graph.add_edge(prev_node, 'V', weight=w, label=w)
        self.graph.add_edge('U', job.operations[0].id, weight=0, label=0)

    def add_disjunctive_edge(self, machine, sequence:list):
        prev_node = (machine.id, sequence.pop(0).id)
        w = self.operations[prev_node].duration
        for job in sequence:
            op_id = (machine.id, job.id)
            self.graph.add_edge(prev_node, op_id, weight=w, label=w)
            self.disjunctive_edges.add((prev_node, op_id))
            prev_node = op_id
            w = self.operations[prev_node].duration

    def remove_disjunctive_edges(self, machine):
        for job1 in self.jobs:
            self.graph.remove_edges_from([((machine.id, job1.id), (machine.id, job2.id)) for job2 in self.jobs if job2 != job1])
            self.disjunctive_edges.difference_update([((machine.id, job1.id), (machine.id, job2.id)) for job2 in self.jobs if job2 != job1])

    def get_nx_graph(self):
        return self.graph
    
    def get_makespan(self):
        return nx.dag_longest_path_length(self.graph)
    
    def plot_graph(self):
        plt.figure(figsize=(10, 6))
        G = self.graph
        edge_labels = nx.get_edge_attributes(G, 'label')
        
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels)
        nx.draw_networkx_nodes(G, self.pos, node_color='lightblue')
        nx.draw_networkx_nodes(G, self.pos, nodelist=['U', 'V'], node_color='blue')

        nx.draw_networkx_edges(G, self.pos)
        nx.draw_networkx_edges(G, self.pos, edgelist=self.disjunctive_edges, edge_color='lightgray', arrows=True)

        nx.draw_networkx_labels(G, self.pos)
        print('makespan: ', self.get_makespan())
        plt.show()
