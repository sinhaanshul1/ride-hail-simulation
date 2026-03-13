


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
        route = self.city.get_route(start[::-1], end[::-1])
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
                order.start_loc
            )
            
            # Hand off to the vehicle
            vehicle.assign_order(order, pickup_route)
            print(f"Dispatched Vehicle {vehicle.vehicle_id} to Order.")
            
        except networkx.exception.NetworkXNoPath:
            print("No path found for dispatch, skipping.")
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
            vehicle.update(self.dt)
        # for vehicle in self.vehicles:
        #     vehicle.update(self.dt)
        #     if vehicle.route_complete():
        #         vehicle.set_route_complete(False)
                
        #         # Update order status based on what just completed
        #         finished_order = vehicle.orders()[0] if vehicle.orders() else None
        #         if finished_order:
        #             if finished_order.status == OrderStatus.ASSIGNED:
        #                 finished_order.pick_up(time=self.time)
        #                 print(f"Order picked up at {self.time}")
        #             elif finished_order.status == OrderStatus.PICKED_UP:
        #                 finished_order.drop_off(time=self.time)
        #                 print(f"Order dropped off at {self.time}")

        #         # Pop the completed route and its order
        #         vehicle.routes().pop(0)
        #         vehicle.orders().pop(0)
        #         vehicle.segment_index = 0
        #         vehicle.segment_progress = 0

        #         # Insert bridging route if needed to reach next route's start
        #         if vehicle.routes() and vehicle.routes()[0]:
        #             next_start = vehicle.routes()[0][0][0].interpolate(0)
        #             at_next_start = (
        #                 abs(vehicle.x() - next_start.x) < 1e-4 and
        #                 abs(vehicle.y() - next_start.y) < 1e-4
        #             )
        #             if not at_next_start:
        #                 try:
        #                     bridge = self.city.get_route(
        #                         (vehicle.y(), vehicle.x()),
        #                         (next_start.y, next_start.x)
        #                     )
        #                     vehicle.routes().insert(0, bridge)
        #                     vehicle.orders().insert(0, None)  # bridging has no order → status stays derived from next real order
        #                 except Exception:
        #                     pass

    # def _update_vehicles(self):
    #     """Update vehicle positions"""
    #     for vehicle in self.vehicles:
    #         vehicle.update(self.dt)
    #         if vehicle.route_complete():
    #             if len(vehicle.routes()) == 0:
    #                 vehicle.set_status(VehicleStatus.IDLE)
    #             elif len(vehicle.routes()) == 1:
    #                 vehicle.routes().pop(0)
    #                 if vehicle.orders():
    #                     vehicle.orders().pop(0)
    #                 vehicle.segment_index = 0
    #                 vehicle.segment_progress = 0
    #                 print('Route complete, no more routes in queue')
    #                 vehicle.set_status(VehicleStatus.IDLE)
    #             else:
    #                 if len(vehicle.orders()) == len(vehicle.routes()):
    #                     vehicle.orders().pop(0)
    #                     vehicle.routes().pop(0)
    #                 else:
    #                     vehicle.routes().pop(0)
    #                 vehicle.segment_index = 0
    #                 vehicle.segment_progress = 0
                    
    #                 # Use a small epsilon for coordinate comparison instead of direct equality
    #                 if abs(vehicle.x() - vehicle.routes()[0][0][0].interpolate(0).x) < 1e-4 and abs(vehicle.y() - vehicle.routes()[0][0][0].interpolate(0).y) < 1e-4:
    #                     vehicle.set_status(VehicleStatus.IN_ROUTE)
    #                     if vehicle.orders():
    #                          vehicle._orders[0].pick_up(time=self.time)
    #                 else:
    #                     vehicle.set_status(VehicleStatus.TO_PICKUP)
    #                     vehicle.routes().insert(0, self.city.get_route((vehicle.y(), vehicle.x()), (vehicle.routes()[0][0][0].interpolate(0).y, vehicle.routes()[0][0][0].interpolate(0).x)))
    #                 vehicle.set_route_complete(False)
    
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

    # def run(self, steps=500, interval=50):
    #     """
    #     Run animated simulation
    #     steps: number of animation frames
    #     interval: ms between frames
    #     """

    #     self.setup_visualization()
    #     x_min, x_max = self.ax.get_xlim()
    #     y_min, y_max = self.ax.get_ylim()

    #     num_vehicles = 100
    #     for i in range(num_vehicles):
    #         x,y = self.city.get_random_point()
    #         self.vehicles.append(Vehicle(x=x, y=y, vehicle_id=i+3, speed_mps=12))
        

    #     for _ in range(1000):
    #         try:
    #             self.vehicles[int(np.random.uniform(0, len(self.vehicles)-1))].assign_route(self.city.get_route((np.random.uniform(y_min, y_max), np.random.uniform(x_min, x_max)), (np.random.uniform(y_min, y_max), np.random.uniform(x_min, x_max))))
    #         except networkx.exception.NetworkXNoPath:
    #             print("No path found for random route, skipping assignment")


    #     anim = FuncAnimation(
    #         self.fig,
    #         self._animate,
    #         frames=steps,
    #         interval=interval,
    #         blit=True
    #     )

    #     plt.show()

# if __name__ == "__main__":
#     city = City()
#     # city.load_city_from_address("1449 Primrose Way, Cupertino, CA", radius=10000)
#     city.load_city_from_address("415 Mission Street, San Francisco, CA", radius=10000)
#     # city.load_city_from_place("San Francisco, CA")
#     vehicles = [
#         Vehicle(x=-122.035953, y=37.297, vehicle_id=1, speed_mps=12),
#         Vehicle(x=0, y=0, vehicle_id=2, speed_mps=12),


#     ]

#     sim = Simulation(city, vehicles)
    

#     # route_geom_1 = city.get_route_by_address("1449 Primrose Way, Cupertino, CA", "10050 S De Anza Blvd, Cupertino, CA")
#     # route_geom_2 = city.get_route_by_address("7658 Normandy Way, Cupertino, CA", "7483 Moltzen Drive, Cupertino, CA")
#     # vehicles[0].assign_route(route_geom_1)
#     # vehicles[0].assign_route(route_geom_2)
#     # vehicles[0].assign_route(city.get_route_by_address("7588 Lockford Court, Cupertino, CA", "7658 Normandy Way, Cupertino, CA"))
#     # vehicles[0].assign_route(city.get_route_by_address("7658 Normandy Way, Cupertino, CA", "7483 Moltzen Drive, Cupertino, CA"))
#     # vehicles[1].assign_route(route_geom_2)
#     sim.run()