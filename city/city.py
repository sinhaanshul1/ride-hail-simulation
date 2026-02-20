from .node import Node
from .edge import Edge
import random
import matplotlib.pyplot as plt
from vehicles import *
import osmnx as ox
import networkx as nx
from termcolor import colored

class City:
    def __init__(self, vehicles=[]):
        # CHAGNE TO GRAPH ADJACENCY LIST REPRESNTATION
        self.graph = None
        self.vehicles = vehicles
    
    def load_city_from_address(self, address, radius=2000):
        self.graph = ox.graph_from_address(address, radius, network_type="drive")
    
    def load_city_from_place(self, location):
        self.graph = ox.graph_from_place(location, network_type="drive")
    
    def add_time_to_edges(self):
        for edge in self.graph.edges(keys=True, data=True):
            try:
                from_node = edge[0]
                to_node = edge[1]
                key = edge[2]
                data = self.graph.edges[from_node, to_node, key]
                speed = int(data['maxspeed'].split()[0])
                distance = data['length']
                self.graph.edges[from_node, to_node, key]['time'] = distance / speed
                print(edge)
            except KeyError:
                print(colored(f"Keys for edge: {str(self.graph.edges[from_node, to_node, key].keys())}", "red"))

    def get_route(self, start, end):
        orig = ox.distance.nearest_nodes(self.graph, start[1], start[0])
        dest = ox.distance.nearest_nodes(self.graph, end[1], end[0])
        return nx.shortest_path(self.graph, orig, dest, weight='time')
        
    def visualize_city(self):
        if self.graph is None:
            print("No graph to visualize. Please load a city first.")
            return
        fig, ax = ox.plot.plot_graph_route(
            self.graph,
            route_color='r',
            route_linewidth=4,
            route_alpha=0.6,
            orig_dest_size=100,
            show=True,
            close=True
        )
        plt.show()

if __name__ == "__main__":
    city = City()
    city.generate_random_city(30, 50)
    city.save_city("random_city.txt")
    print("Random city generated and saved to random_city.txt")
    city.visualize_city()