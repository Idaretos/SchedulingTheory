from SBnetwork import *
from lower_bound_PEDD import *
from collections import defaultdict
import heapq
from networkx.classes.function import path_weight

class SBNode(object): # Shifting Bottleneck Node
    def __init__(self, predetermined, level, superJ:set, t, lower_bound)->None:
        self.id = tuple(predetermined)
        self.predetermined = predetermined
        self.level = level
        self.J = superJ - set(predetermined)
        self.t = t
        self.lower_bound = 0
        self.Lmax = -1e9 if len(predetermined) < len(superJ) else lower_bound
        self.preempted = True

    def __lt__(self, other):
        return self.lower_bound < other.lower_bound
    
    def __gt__(self, other):
        return self.lower_bound > other.lower_bound
    
    def __eq__(self, other):
        return self.lower_bound == other.lower_bound

class SBNQueue(object): # Shifting Bottleneck Node Queue
    # Priority Queue of SBNodes, sorted by lower_bound
    def __init__(self, mlp_table)->None:
        self.mlp_table = mlp_table
        self.nodes = []

    def put(self, node)->None:
        heapq.heappush(self.nodes, node)
    
    def remove(self, node) -> None:
        self.nodes.remove(node)

    def get(self) -> SBNode:
        return heapq.heappop(self.nodes)
    
    def __len__(self)->int:
        return len(self.nodes)
    
    def __getitem__(self, index)->SBNode:
        return self.nodes.queue[index]
    
    def is_empty(self)->bool:
        return len(self.nodes) == 0

def compute_Cmax(G: SBN) -> None:
    Cmax = nx.dag_longest_path_length(G.graph)
    return Cmax

def single_machine_schedule(G, machine, mlp_table) -> list:
    # using branch and bound algorithm
    # finds out the optimal sequence in terms of maximum lateness for a single machine

    # Each node represents a partial schedule
    # Each node has a predetermined sequence of jobs
    # mlp_table = {job: (proc_t, release_t, due_t)}

    # nodes: priority queue of nodes
    # threshold: feasible lower bound so far
    # superJ: set of all jobs
    # level: level of the node

    nodes = SBNQueue(mlp_table)
    threshold = float('inf')
    superJ = set([job for job in G.jobs if (machine.id, job.id) in G.operations.keys()])
    
    def update_threshold(mlp_table, predetermined, th):
        preempted, l_bound, sequence, span, predet_t = get_lower_bound(mlp_table, predetermined)
        if not preempted:
            th = min(th, l_bound)
            if l_bound <= threshold: # current sequence is better than the previous one
                nodes.put(SBNode(sequence, len(superJ), superJ, span, l_bound))
        elif l_bound <= threshold: # current sequence is not feasible, but it is still a candidate
            nodes.put(SBNode(predetermined, len(superJ), superJ, predet_t, l_bound))
        return th


    def node_traversal(node:SBNode, mlp_table:dict, nodes:SBNQueue, threshold) -> None:
        if node.lower_bound > threshold:
            return
        level = node.level + 1
        if level == len(mlp_table): # all jobs are scheduled
            return
        for c in node.J:
            r_c = mlp_table[c][1]
            if len(node.J) == 1 or r_c < min([max(node.t, mlp_table[l][1]) + mlp_table[l][0] for l in node.J-set([c])]): # if any l can be scheduled before c, then c is not a candidate
                threshold = update_threshold(mlp_table, node.predetermined+[c], threshold)

    # initialize nodes
    for job in superJ:
        threshold = update_threshold(mlp_table, [job], threshold)

    Lmax = int(1e9)
    arg_Lmax = None

    while not nodes.is_empty():
        node = nodes.get()
        if node.level == len(superJ):
            # all jobs are scheduled
            if node.Lmax <= threshold:
                threshold = node.lower_bound
            if node.Lmax < Lmax:
                Lmax = node.Lmax
                arg_Lmax = node.predetermined
            continue
        node_traversal(node, mlp_table, nodes, threshold)

    return Lmax, arg_Lmax

def longest_path_weight(G, source, sink, weight='weight'):
    max_path = max(nx.all_simple_paths(G, source, sink), key=lambda x: len(x))
    return path_weight(G, max_path, weight=weight)

def print_mlp_table(machine, mlp_table):
    print(machine.name)
    for job in mlp_table.keys():
        print(job, mlp_table[job])

def shifting_bottleneck(G: SBN):
    Cmax = compute_Cmax(G)
    M  = set(G.machines)
    M0 = set()
    
    while M-M0:
        h = None
        Lmax = -int(1e9)
        sequence = None

        for machine in M-M0:
            mlp_table = defaultdict(list)
            for job in G.jobs:
                if (machine.id, job.id) in G.operations.keys():
                    mlp_table[job].append(G.operations[(machine.id, job.id)].duration)
                    mlp_table[job].append(longest_path_weight(G.graph, 'U', (machine.id, job.id), weight='weight'))
                    mlp_table[job].append(Cmax + G.operations[(machine.id, job.id)].duration - longest_path_weight(G.graph, (machine.id, job.id), 'V', weight='weight'))                    
                
            Lmax_machine, sequence_machine = single_machine_schedule(G, machine, mlp_table)
            if Lmax_machine > Lmax:
                Lmax = Lmax_machine
                h = machine
                sequence = sequence_machine
            elif Lmax_machine == Lmax:
                if machine.id < h.id:
                    h = machine
                    sequence = sequence_machine
        if sequence is None:
            break
        G.add_disjunctive_edge(h, sequence)
        M0.add(h)

        for machine in M0-set([h]):
            mlp_table = defaultdict(list)
            # delete added disjunctive edges for all (machine.id, x.id) -> (machine.id, y.id)
            G.remove_disjunctive_edges(machine)
            for job in G.jobs:
                if (machine.id, job.id) in G.operations.keys():
                    mlp_table[job].append(G.operations[(machine.id, job.id)].duration)
                    mlp_table[job].append(longest_path_weight(G.graph, 'U', (machine.id, job.id), weight='weight'))
                    mlp_table[job].append(Cmax + G.operations[(machine.id, job.id)].duration - longest_path_weight(G.graph, (machine.id, job.id), 'V', weight='weight'))

            Lmax_machine, sequence_machine = single_machine_schedule(G, machine, mlp_table)
            G.add_disjunctive_edge(machine, sequence_machine)

    return G







