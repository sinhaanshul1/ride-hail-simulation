import random
from .vehicle_status import VehicleStatus

class Vehicle:
    def __init__(self, vehicle_id, x, y, capacity=4, status=VehicleStatus.IDLE):
        self.vehicle_id = vehicle_id
        self.x = x
        self.y = y
        self.capacity = capacity
        self.status = status
        self.color = self._get_color()
    
    def _get_color(self):
        if self.status == VehicleStatus.IDLE:
            return 'green'
        elif self.status == VehicleStatus.TO_PICKUP:
            return 'yellow'
        elif self.status == VehicleStatus.IN_ROUTE:
            return 'blue'
        elif self.status == VehicleStatus.OFFLINE:
            return 'red'
    
    def __str__(self):
        return f"Vehicle({self.vehicle_id}, ({self.x}, {self.y}), capacity={self.capacity}, status={self.status})"
    