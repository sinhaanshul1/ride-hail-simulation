from node import Node
from edge import Edge

class City:
    def __init__(self, nodes={}, edges=[]):
        self.nodes = nodes
        self.edges = edges
    
    def add_node(self, node):
        self.nodes[node.id] = node
    
    def add_edge(self, edge):
        self.edges.append(edge)

    def save_city(self, filename="city.txt"):
        with open(filename, 'w') as f:
            for node in self.nodes:
                f.write(f"NODE {node.id} {node.x} {node.y}\n")
            for edge in self.edges:
                f.write(f"EDGE {edge.start_node.id} {edge.end_node.id} {edge.weight}\n")
    
    def load_city(self, filename="city.txt"):
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts[0] == "NODE":
                    _, id, x, y = parts
                    self.add_node(Node(id, float(x), float(y)))
                elif parts[0] == "EDGE":
                    _, start_id, end_id, weight = parts
                    start_node = self.nodes[start_id]
                    end_node = self.nodes[end_id]
                    self.add_edge(Edge(start_node, end_node, float(weight)))
