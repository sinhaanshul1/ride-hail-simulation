


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx
import numpy as np
from model import City, Vehicle, VehicleStatus, Order, OrderStatus


class Simulation:
    def __init__(self, city: City, vehicles: list[Vehicle], dt=0.05):
        """
        city: City object
        vehicles: list[Vehicle]
        dt: simulation timestep (seconds)
        """
        self.city = city
        self.vehicles = vehicles
        self.orders = []
        self.dt = dt
        self.time = 0.0

        # matplotlib handles
        self.fig = None
        self.ax = None
        self.scatter = None
    
    @property
    def idle_vehicles(self):
        """Dynamically returns a list of vehicles currently in the IDLE state."""
        return [v for v in self.vehicles if v.status == VehicleStatus.IDLE]
        
    @property
    def unassigned_orders(self):
        """You can do the exact same thing for your orders!"""
        return [o for o in self.orders if o.status == OrderStatus.REQUESTED]

    def step(self):
        """Advance simulation by one timestep"""
        # self.time += self.dt
        # if len(self.vehicles[0].orders()) < 2:

        #     self._assign_orders()
        # self._update_vehicles()
        self.time += self.dt
        
        # 1. Spawn demand (e.g., 10% chance per tick)
        if np.random.uniform(0, 1) < 0.1: 
            self._create_random_order()
            
        # 2. Match supply and demand
        self._dispatch()
        
        # 3. Move the world
        self._update_vehicles()

    def _create_random_order(self):
        """Create a new order with random start/end and assign to random vehicle"""
        start = self.city.get_random_point()
        end = self.city.get_random_point()
        try:
            route = self.city.get_route(start[::-1], end[::-1])
        except networkx.exception.NetworkXNoPath:
            print("No path found for new random order, skipping creation")
            return
        order = Order(start_loc=start, end_loc=end, creation_time=self.time, route=route)

        self.orders.append(order)
    
    def _dispatch(self):
        # Grab the temporary lists of who is available
        waiting_orders = self.unassigned_orders
        available_cars = self.idle_vehicles

        if not waiting_orders or not available_cars:
            return # Nothing to do

        order = waiting_orders[0] # Just look at the first one
        vehicle = available_cars[0]

        try:
            # Dispatcher calculates the pickup route
            pickup_route = self.city.get_route(
                (vehicle._y, vehicle._x), # Assuming your city expects (lat, lon)
                order.start_loc[::-1]
            )
            
            # Hand off to the vehicle
            vehicle.assign_order(order, pickup_route, time=self.time)
            print(f"Dispatched Vehicle {vehicle.vehicle_id} to Order.")
            
        except networkx.exception.NetworkXNoPath:
            print("No path found for getting to the pickup location, skipping.")
            # Note: In a real system, you'd mark this order as 'UNROUTABLE' 
            # so it doesn't block the queue forever.
        # # 1. Find a match (Order + Idle Vehicle)
        # if not self.unassigned_orders:
        #     print("No unassigned orders, skipping dispatch")
        #     return
        # order = self.unassigned_orders.pop(0)
        # if not self.idle_vehicles:
        #     print("No idle vehicles available, cannot assign order")
        #     return
        # vehicle = self.idle_vehicles.pop(0)

        # # 2. Dispatcher calculates the pickup route using the City
        # # Note: Handle the [::-1] flip here if your get_route needs it!
        # pickup_route = self.city.get_route(vehicle.location, order.start_loc)

        # # 3. Dispatcher hands BOTH the order and the pickup route to the vehicle
        # vehicle.assign_order(order, pickup_route)
        # return

    
    def _update_vehicles(self):
        for vehicle in self.vehicles:
            vehicle.update(self.dt, self.time)

    def _assign_orders(self):
        if np.random.uniform(0, 1) < 0.1: # 10% chance of new order each step
            start = self.city.get_random_point()
            end = self.city.get_random_point()
            route = self.city.get_route(start[::-1], end[::-1])
            order = Order(start_loc=start, end_loc=end, creation_time=self.time, route=route)

            self.orders.append(order)
            random_vehicle = self.vehicles[int(np.random.uniform(0, len(self.vehicles)-1))]
            random_vehicle.assign_order(order)
            # random_vehicle.assign_routeroute)
            order.assign_vehicle(random_vehicle, time=self.time)
    
    def get_vehicle_data(self):
        """Extract data formatted for PyDeck/Pandas"""
        data = []
        # PyDeck needs RGB arrays, so we map your string colors
        color_map = {
            'red': [255, 0, 0, 200],
            'green': [0, 255, 0, 200],
            'blue': [0, 0, 255, 200],
            'yellow': [255, 255, 0, 200],
            'grey': [128, 128, 128, 200]
        }
        
        for v in self.vehicles:
            if v.x() is not None and v.y() is not None:
                data.append({
                    "id": v.vehicle_id,
                    "lon": v.x(), # Note: x is lon, y is lat
                    "lat": v.y(),
                    "status": str(v.status),
                    "color": color_map.get(v.color, [255, 255, 255, 200])
                })
        return data
    
    def get_order_data(self):
        """Extract order data for visualization/metrics"""
        data = []
        for o in self.orders:
            data.append({
                "start_lon": o.start_loc[1],
                "start_lat": o.start_loc[0],
                "end_lon": o.end_loc[1],
                "end_lat": o.end_loc[0],
                "status": str(o.status),
                "creation_time": o.creation_time,
                "pickup_time": o.pickup_time,
                "dropoff_time": o.dropoff_time
            })
        # print(len(data), "orders in get_order_data")
        return data


    def setup_visualization(self):
        """Draw static city + initialize vehicle markers"""
        self.fig, self.ax = self.city.visualize_city()

        self.scatter = self.ax.scatter(
            [],
            [],
            s=30,
            c=[],
            facecolors=[],
            zorder=5
        )

    def _get_vehicle_positions(self):
        """Extract (x, y) positions for all active vehicles"""
        positions = []
        colors = []

        for v in self.vehicles:
            if v.x() is not None and v.y() is not None:
                positions.append((v.x(), v.y()))
                colors.append(v.color)

        return (
            np.array(positions) if positions else np.empty((0, 2)),
            colors if colors else []
        )

    def _animate(self, frame):
        """Animation callback"""
        self.step()

        positions, colors = self._get_vehicle_positions()
        self.scatter.remove()
        if len(positions) > 0:
            self.scatter = self.ax.scatter(
                positions[:, 0],
                positions[:, 1],
                s=30,
                c=colors,
                zorder=5
            )
        else:
            self.scatter = self.ax.scatter([], [], s=30, c=[], zorder=5)

        return (self.scatter,)