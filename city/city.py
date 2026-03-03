
import random
import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from termcolor import colored
from shapely.geometry import LineString, MultiLineString
import shapely

class City:
    def __init__(self, vehicles=[]):
        # CHAGNE TO GRAPH ADJACENCY LIST REPRESNTATION
        self.graph = None
        self._route = None
    
    def load_city_from_address(self, address, radius=2000):
        print(colored(f"Loading city from address: {address} with radius: {radius} meters", "green"))
        try:
            self.graph = ox.graph_from_address(address, radius, network_type="drive")
        except Exception as e:
            print(colored(f"Error occurred while loading city from address: {e}", "red"))
            exit()
        print(colored("City loaded successfully", "green"))
        self.add_time_to_edges()
    
    def load_city_from_place(self, location):
        print(colored(f"Loading city from place: {location}", "green"))
        try:
            self.graph = ox.graph_from_place(location, network_type="drive")
        except Exception as e:
            print(colored(f"Error occurred while loading city from place: {e}", "red"))
            exit()
        print(colored("City loaded successfully", "green"))
        self.add_time_to_edges()

    def print_nodes(self):
        if self.graph is None:
            print("Graph not loaded yet")
            return
        for node in self.graph.nodes(data=True):
            print(node)
    
    def print_edges(self):
        if self.graph is None:
            print("Graph not loaded yet")
            return
        for edge in self.graph.edges(keys=True, data=True):
            print(edge)
    
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
                # print(edge)
            except KeyError:
                print(colored(f"Keys for edge: {str(self.graph.edges[from_node, to_node, key].keys())}", "red"))
            except AttributeError:
                print(colored(f"Maxspeed: {str(self.graph.edges[from_node, to_node, key]['maxspeed'])}", "blue"))

    def get_route_by_address(self, start, end):
        start = ox.geocode(start)
        end = ox.geocode(end)
        return self.get_route(start, end)
    
    def old_get_route(self, start_lat_long, end_lat_long):
        orig = ox.distance.nearest_nodes(self.graph, start_lat_long[1], start_lat_long[0])
        dest = ox.distance.nearest_nodes(self.graph, end_lat_long[1], end_lat_long[0])
        route = nx.shortest_path(self.graph, orig, dest, weight='time')
        path = []
        for from_node, to_node in zip(route[:-1], route[1:]):
            try:
                edge_data = self.graph.get_edge_data(from_node, to_node)[0]["geometry"]
                path.append(edge_data)
            except KeyError:
                x1, y1 = self.graph.nodes[from_node]["x"], self.graph.nodes[from_node]["y"]
                x2, y2 = self.graph.nodes[to_node]["x"], self.graph.nodes[to_node]["y"]
                line = LineString([(x1, y1), (x2, y2)])
                path.append(line)
            # print(edge_data)
        self._route = shapely.line_merge(MultiLineString(path))

        # print(route)
        # return path
        return self._route
    
    def get_route(self, start_lat_long, end_lat_long):
        orig = ox.distance.nearest_nodes(self.graph, start_lat_long[1], start_lat_long[0])
        dest = ox.distance.nearest_nodes(self.graph, end_lat_long[1], end_lat_long[0])
        route = nx.shortest_path(self.graph, orig, dest, weight='time')
        path = []
        for from_node, to_node in zip(route[:-1], route[1:]):
            try:
                edge_data = self.graph.get_edge_data(from_node, to_node)[0]["geometry"]
                max_speed = self._parse_maxspeed(self.graph.get_edge_data(from_node, to_node)[0]["maxspeed"])
                path.append((edge_data, max_speed))
            except KeyError:
                x1, y1 = self.graph.nodes[from_node]["x"], self.graph.nodes[from_node]["y"]
                x2, y2 = self.graph.nodes[to_node]["x"], self.graph.nodes[to_node]["y"]
                line = LineString([(x1, y1), (x2, y2)])
                path.append((line, 25))
            # print(edge_data)
        # self._route = shapely.line_merge(MultiLineString(path))

        # print(route)
        # return path
        return path
    
    def _parse_maxspeed(self, maxspeed):
        if isinstance(maxspeed, list):
            maxspeed = maxspeed[0]
        try:
            return int(maxspeed.split()[0])
        except (ValueError, AttributeError):
            return 25  # Default speed if parsing fails
    
    
    def plot_geometry(self, ax, geom, **kwargs):
        if isinstance(geom, LineString):
            xs, ys = geom.xy
            print(xs, ys)
            ax.plot(xs, ys, **kwargs)

        elif isinstance(geom, MultiLineString):
            for line in geom.geoms:
                xs, ys = line.xy
                ax.plot(xs, ys, **kwargs)

        
    def visualize_city(self):
        if self.graph is None:
            print("No graph to visualize. Please load a city first.")
            return

        fig, ax = ox.plot_graph(
            self.graph,
            node_size=0,
            edge_color="#A0A0A0",
            edge_linewidth=1,
            show=False,
            close=False,
            bgcolor='white',
        )
        fig.tight_layout(pad=0)
        ax.set_position([0, 0, 1, 1])

        return fig, ax
    def get_random_point(self):
        node = random.choice(list(self.graph.nodes))
        x = self.graph.nodes[node]['x']
        y = self.graph.nodes[node]['y']
        return x, y

if __name__ == "__main__":
    city = City()
    city.load_city_from_address("1449 Primrose Way, Cupertino, CA")
    city.print_nodes()
    city.print_edges()
    city.visualize_city()