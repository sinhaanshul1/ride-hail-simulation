import enum

class OrderStatus(enum.Enum):
    REQUESTED = 1
    ASSIGNED = 2
    PICKED_UP = 3
    DROPPED_OFF = 4
    CANCELLED = 5


class Order:
    def __init__(self, start_loc, end_loc, creation_time, route, pickup_time=None, dropoff_time=None):
        self.start_loc = start_loc
        self.end_loc = end_loc
        self.creation_time = creation_time
        self.route = route
        self.pickup_time = pickup_time
        self.dropoff_time = dropoff_time
        self.assigned_vehicle = None
        self.status = OrderStatus.REQUESTED
    
    def set_status(self, status):
        self.status = status
    
    def assign_vehicle(self, vehicle, time=None):
        self.assigned_vehicle = vehicle
        self.assign_time = time
        self.status = OrderStatus.ASSIGNED

    def pick_up(self, time=None):
        self.status = OrderStatus.PICKED_UP
        self.pickup_time = time
    
    def drop_off(self, time=None):
        self.status = OrderStatus.DROPPED_OFF
        self.dropoff_time = time
    
    def cancel(self):
        self.status = OrderStatus.CANCELLED