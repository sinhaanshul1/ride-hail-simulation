


import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx
import numpy as np
from model import City, Vehicle, VehicleStatus, Order


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

    def step(self):
        """Advance simulation by one timestep"""
        self.time += self.dt
        # PICK A RANDOM NUMBER AND IF IT IS BELOW A THRESHOLD, CREATE A NEW ORDER
        # ASSIGN IT TO A RANDOM VEHICLE
        if np.random.uniform(0, 1) < 0.1: # 10% chance of new order each step
            start = self.city.get_random_point()
            end = self.city.get_random_point()
            route = self.city.get_route(start[::-1], end[::-1])
            order = Order(start_loc=start, end_loc=end, creation_time=self.time, route=route)
            self.orders.append(order)
            random_vehicle = self.vehicles[int(np.random.uniform(0, len(self.vehicles)-1))]
            random_vehicle.assign_route(route)
            order.assign_vehicle(random_vehicle)
        for vehicle in self.vehicles:
            vehicle.update(self.dt)
            if vehicle.route_complete():
                if len(vehicle.routes()) == 0:
                    vehicle.set_status(VehicleStatus.IDLE)
                elif len(vehicle.routes()) == 1:
                    vehicle.routes().pop(0)
                    vehicle.segment_index = 0
                    vehicle.segment_progress = 0
                    print('Route complete, no more routes in queue')
                    vehicle.set_status(VehicleStatus.IDLE)
                else:
                    vehicle.routes().pop(0)
                    vehicle.segment_index = 0
                    vehicle.segment_progress = 0
                    if vehicle.x() == vehicle.routes()[0][0][0].interpolate(0).x and vehicle.y() == vehicle.routes()[0][0][0].interpolate(0).y:
                        vehicle.set_status(VehicleStatus.IN_ROUTE)
                    else:
                        vehicle.set_status(VehicleStatus.TO_PICKUP)
                        vehicle.routes().insert(0, self.city.get_route((vehicle.y(), vehicle.x()), (vehicle.routes()[0][0][0].interpolate(0).y, vehicle.routes()[0][0][0].interpolate(0).x)))
                    vehicle.set_route_complete(False)
    
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

    def run(self, steps=500, interval=50):
        """
        Run animated simulation
        steps: number of animation frames
        interval: ms between frames
        """

        self.setup_visualization()
        x_min, x_max = self.ax.get_xlim()
        y_min, y_max = self.ax.get_ylim()

        num_vehicles = 100
        for i in range(num_vehicles):
            x,y = self.city.get_random_point()
            self.vehicles.append(Vehicle(x=x, y=y, vehicle_id=i+3, speed_mps=12))
        

        for _ in range(1000):
            try:
                self.vehicles[int(np.random.uniform(0, len(self.vehicles)-1))].assign_route(self.city.get_route((np.random.uniform(y_min, y_max), np.random.uniform(x_min, x_max)), (np.random.uniform(y_min, y_max), np.random.uniform(x_min, x_max))))
            except networkx.exception.NetworkXNoPath:
                print("No path found for random route, skipping assignment")


        anim = FuncAnimation(
            self.fig,
            self._animate,
            frames=steps,
            interval=interval,
            blit=True
        )

        plt.show()

if __name__ == "__main__":
    city = City()
    # city.load_city_from_address("1449 Primrose Way, Cupertino, CA", radius=10000)
    city.load_city_from_address("415 Mission Street, San Francisco, CA", radius=10000)
    # city.load_city_from_place("San Francisco, CA")
    vehicles = [
        Vehicle(x=-122.035953, y=37.297, vehicle_id=1, speed_mps=12),
        Vehicle(x=0, y=0, vehicle_id=2, speed_mps=12),


    ]

    sim = Simulation(city, vehicles)
    

    # route_geom_1 = city.get_route_by_address("1449 Primrose Way, Cupertino, CA", "10050 S De Anza Blvd, Cupertino, CA")
    # route_geom_2 = city.get_route_by_address("7658 Normandy Way, Cupertino, CA", "7483 Moltzen Drive, Cupertino, CA")
    # vehicles[0].assign_route(route_geom_1)
    # vehicles[0].assign_route(route_geom_2)
    # vehicles[0].assign_route(city.get_route_by_address("7588 Lockford Court, Cupertino, CA", "7658 Normandy Way, Cupertino, CA"))
    # vehicles[0].assign_route(city.get_route_by_address("7658 Normandy Way, Cupertino, CA", "7483 Moltzen Drive, Cupertino, CA"))
    # vehicles[1].assign_route(route_geom_2)
    sim.run()