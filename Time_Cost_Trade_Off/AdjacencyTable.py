from typing import List, Dict, Tuple

class AdjacencyTable(object):
    def __init__(self):
        self.graph = {}

    def add_vertex(self, vertex):
        """Add a vertex to the graph."""
        if vertex not in self.graph:
            self.graph[vertex] = set()

    def add_edge(self, vertex1, vertex2):
        """Add an edge between vertex1 and vertex2."""
        self.add_vertex(vertex1)
        self.add_vertex(vertex2)
        self.graph[vertex1].add(vertex2)

    def remove_edge(self, vertex1, vertex2):
        """Remove the edge between vertex1 and vertex2."""
        if vertex1 in self.graph and vertex2 in self.graph:
            self.graph[vertex1].remove(vertex2)

    def remove_vertex(self, vertex):
        """Remove a vertex and its associated edges."""
        if vertex in self.graph:
            for neighbor in list(self.graph[vertex]):
                self.remove_edge(vertex, neighbor)
            del self.graph[vertex]

    def get_neighbors(self, vertex):
        """Return a set of neighbors of the given vertex."""
        return self.graph.get(vertex, set())
    
    def is_reachable(self, start_vertex, target_vertex, constraint_set=set()):
        """Check if target_vertex is reachable from start_vertex using DFS, while avoiding vertices in constraint_set."""
        visited = set()
        return self._constraint_dfs(start_vertex, target_vertex, visited, constraint_set)

    def _constraint_dfs(self, current_vertex, target_vertex, visited, constraint_set):
        """Helper method to perform DFS with constraints."""
        if current_vertex == target_vertex:
            return True
        if current_vertex in visited or current_vertex in constraint_set or target_vertex in constraint_set:
            return False
        visited.add(current_vertex)
        for neighbor in self.graph[current_vertex]:
            if self._constraint_dfs(neighbor, target_vertex, visited, constraint_set):
                return True
        return False