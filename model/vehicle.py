import random
from .vehicle_status import VehicleStatus
from .city import City


COLORS = {VehicleStatus.IDLE: 'red', VehicleStatus.TO_PICKUP: 'yellow', VehicleStatus.IN_ROUTE: 'green', VehicleStatus.OFFLINE: 'grey'}


class Vehicle:
    def __init__(self, vehicle_id, x, y, capacity=4, status=VehicleStatus.IDLE, speed_mps=0.00000000000001):
        self.vehicle_id = vehicle_id
        self._x = x
        self._y = y
        self.capacity = capacity
        self.status = status
        self.speed_mps = speed_mps
        self._routes = []
        self.color = self._get_color()
        self._route_complete = False
        self.distance_traveled = 0
        self.segment_index = 0
        self.segment_progress = 0
    def routes(self):
        return self._routes

    def x(self):
        return self._x
    
    def y(self):
        return self._y
    
    def route_complete(self):
        return self._route_complete

    def set_route_complete(self, value):
        self._route_complete = value

    def set_status(self, status):
        self.status = status
        self.color = self._get_color()
    
    def update(self, dt):
        if self._routes:
            segment, speed = self._routes[0][self.segment_index]
            self.segment_progress += speed / 11000 * dt
            self.segment_progress = min(self.segment_progress, segment.length)
            position = segment.interpolate(self.segment_progress)
            self._x = position.x
            self._y = position.y
            # print("Distance travelled: ", self.distance_traveled, "Length of route: ", self._routes[0].length)
            if self.segment_progress >= segment.length:
                self.segment_index += 1
                self.segment_progress = 0
                if self.segment_index >= len(self._routes[0]):
                    self._route_complete = True
                    self.distance_traveled = 0
                    self.segment_index = 0
        # # if self.status == VehicleStatus.IN_ROUTE:
        # if self._routes:
        #     self.distance_traveled += self.speed_mps * dt
        #     self.distance_traveled = min(self.distance_traveled, self._routes[0].length)
        #     position = self._routes[0].interpolate(self.distance_traveled)
        #     self._x = position.x
        #     self._y = position.y
        #     # print("Distance travelled: ", self.distance_traveled, "Length of route: ", self._routes[0].length)
        #     if self.distance_traveled >= self._routes[0].length:
        #         self._route_complete = True
        #         self.distance_traveled = 0

    def _get_color(self):
        if self.status == VehicleStatus.IDLE:
            return 'green'
        elif self.status == VehicleStatus.TO_PICKUP:
            return 'yellow'
        elif self.status == VehicleStatus.IN_ROUTE:
            return 'blue'
        elif self.status == VehicleStatus.OFFLINE:
            return 'red'
    
    def assign_route(self, route: list):
        # print('route: ', route)
        self._routes.append(route)
        self.status = VehicleStatus.IN_ROUTE
        self.color = self._get_color()
        self.distance_traveled = 0
        self.segment_index = 0
        self.segment_progress = 0
        # print(self._routes)
        self.position = self._routes[0][0][0].interpolate(0)
        
    
    def __str__(self):
        return f"Vehicle({self.vehicle_id}, ({self.x}, {self.y}), capacity={self.capacity}, status={self.status})"
    