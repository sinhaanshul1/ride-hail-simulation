from .node import Node
from .edge import Edge
import random
import matplotlib.pyplot as plt
from vehicles import *

class City:
    def __init__(self, nodes={}, edges=[], width=1, height=1, vehicles=[]):
        # CHAGNE TO GRAPH ADJACENCY LIST REPRESNTATION
        self.nodes = nodes
        self.edges = edges
        self.width = width
        self.height = height
        self.vehicles = vehicles
    
    def add_node(self, node):
        self.nodes[node.id] = node
    
    def add_edge(self, edge):
        self.edges.append(edge)

    def save_city(self, filename="city.txt"):
        with open(filename, 'w') as f:
            for node in self.nodes.values():
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
    
    def generate_random_city(self, num_nodes, num_edges, num_vehicles=10):
        for i in range(num_nodes):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            self.add_node(Node(str(i), x, y))
        
        for _ in range(num_edges):
            start_node = random.choice(list(self.nodes.values()))
            end_node = random.choice(list(self.nodes.values()))
            while end_node == start_node:
                end_node = random.choice(list(self.nodes.values()))
            weight = ((start_node.x - end_node.x) ** 2 + (start_node.y - end_node.y) ** 2) ** 0.5
            self.add_edge(Edge(start_node, end_node, weight))
        
        for i in range(num_vehicles):
            self.vehicles.append(Vehicle(str(i), random.uniform(0, self.width), random.uniform(0, self.height)))
    
    def generate_grid_city(self, width, height, width_interval, heigh_interval):
        node_id = 0
        self.width = width
        self.height = height
        for x in range(0, width, width_interval):
            for y in range(0, height, heigh_interval):
                self.add_node(Node(str(node_id), x, y))
                node_id += 1
            
        
    
    def visualize_city(self):
        plt.figure(figsize=(self.width * 10, self.height * 10))
        for edge in self.edges:
            x_values = [edge.start_node.x, edge.end_node.x]
            y_values = [edge.start_node.y, edge.end_node.y]
            plt.plot(x_values, y_values, 'k-', lw=0.5)
        
        for node in self.nodes.values():
            plt.plot(node.x, node.y, 'ro')

        for vehicle in self.vehicles:
            plt.plot(vehicle.x, vehicle.y, color=vehicle.color, marker='s', markersize=10)
        
        plt.title("City Visualization")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.grid()
        plt.show()

if __name__ == "__main__":
    city = City()
    city.generate_random_city(30, 50)
    city.save_city("random_city.txt")
    print("Random city generated and saved to random_city.txt")
    city.visualize_city()