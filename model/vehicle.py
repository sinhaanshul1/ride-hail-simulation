from model.order import OrderStatus
from .vehicle_status import VehicleStatus

class Vehicle:
    def __init__(self, vehicle_id, x, y, capacity=4, speed_mps=0.00000000000001):
        self.vehicle_id = vehicle_id
        
        # Spatial attributes
        self._x = x
        self._y = y
        self.speed_mps = speed_mps
        
        # FSM State
        self.status = VehicleStatus.IDLE 
        self.current_order = None
        self.active_route = []
        
        # Movement tracking
        self.distance_traveled = 0
        self.segment_index = 0
        self.segment_progress = 0
    
    def x(self):
        return self._x
    def y(self):
        return self._y

    @property
    def color(self):
        """Dynamically return color based on current FSM state."""
        if self.status == VehicleStatus.IDLE: return 'green'
        if self.status == VehicleStatus.TO_PICKUP: return 'yellow'
        if self.status == VehicleStatus.IN_ROUTE: return 'blue'
        if self.status == VehicleStatus.OFFLINE: return 'grey'
        return 'green'

    def assign_order(self, order, pickup_route):
        """Handoff from the Dispatcher to the Vehicle."""
        self.current_order = order
        self.active_route = pickup_route
        
        self.status = VehicleStatus.TO_PICKUP
        
        self.current_order.set_status(OrderStatus.ASSIGNED)
        self.current_order.assign_vehicle(self)
        
        # Reset movement trackers for the new route
        self.segment_index = 0
        self.segment_progress = 0

    def update(self, dt):
        """Advances the vehicle along its active route by dt."""
        if self.status == VehicleStatus.IDLE or not self.active_route:
            return

        # 1. Handle physical movement along the current route segment
        segment, speed = self.active_route[self.segment_index]
        self.segment_progress += (speed / 11000) * dt
        self.segment_progress = min(self.segment_progress, segment.length)
        
        position = segment.interpolate(self.segment_progress)
        self._x = position.x
        self._y = position.y

        # 2. Check if we finished the current segment
        if self.segment_progress >= segment.length:
            self.segment_index += 1
            self.segment_progress = 0
            
            # 3. Check if we finished the ENTIRE route
            if self.segment_index >= len(self.active_route):
                self._handle_route_completion()

    def _handle_route_completion(self):
        """Internal FSM logic for when a route ends."""
        if self.status == VehicleStatus.TO_PICKUP:
            # Arrived at pickup! Transition to trip route.
            self.current_order.pick_up() 
            self.status = VehicleStatus.IN_ROUTE
            
            self.active_route = self.current_order.route # Swap to trip route
            self.segment_index = 0
            self.segment_progress = 0
            
        elif self.status == VehicleStatus.IN_ROUTE:
            # Arrived at dropoff! Transition to idle.
            self.current_order.drop_off()
            self.status = VehicleStatus.IDLE
            
            self.active_route = []
            self.current_order = None # Now it is safe to forget the order!

    def __str__(self):
        return f"Vehicle({self.vehicle_id}, ({self._x:.4f}, {self._y:.4f}), status={self.status})"



# import random

# from model.order import OrderStatus
# from .vehicle_status import VehicleStatus
# from .city import City


# COLORS = {VehicleStatus.IDLE: 'red', VehicleStatus.TO_PICKUP: 'yellow', VehicleStatus.IN_ROUTE: 'green', VehicleStatus.OFFLINE: 'grey'}


# class Vehicle:
#     def __init__(self, vehicle_id, x, y, capacity=4, status=VehicleStatus.IDLE, speed_mps=0.00000000000001):
#         self.vehicle_id = vehicle_id
#         self._x = x
#         self._y = y
#         self.capacity = capacity
#         self._status = status
#         self.speed_mps = speed_mps
#         self._routes = []
#         # self.color = self._get_color()
#         self._route_complete = False
#         self.distance_traveled = 0
#         self.segment_index = 0
#         self.segment_progress = 0
#         self._orders = []
#         self.active_route = None
#         self.current_order = None

#     def status(self):
#         # if not self._orders or self._orders[0] is None:
#         if self.current_order is None and self.active_route is None:
#             return VehicleStatus.IDLE
#         # order_status = self._orders[0].status
#         # print(f"Vehicle {self.vehicle_id} order status: {order_status}")
#         if self.current_order is not None:
#             if self.current_order.status == OrderStatus.ASSIGNED:
#                 return VehicleStatus.TO_PICKUP
#         elif self.current_order is not None and self.current_order.status == OrderStatus.PICKED_UP:
#             return VehicleStatus.IN_ROUTE
#         else:
#             return VehicleStatus.IDLE

#     # @property
#     def color(self):
#         s = self.status
#         if s == VehicleStatus.IDLE:
#             return 'green'
#         elif s == VehicleStatus.TO_PICKUP:
#             return 'yellow'
#         elif s == VehicleStatus.IN_ROUTE:
#             return 'blue'
#         return 'green'
    
#     def orders(self):
#         return self._orders
    

#     def routes(self):
#         return self._routes

#     def x(self):
#         return self._x
    
#     def y(self):
#         return self._y
    
#     def route_complete(self):
#         return self._route_complete

#     def set_route_complete(self, value):
#         self._route_complete = value

#     def set_status(self, status):
#         self.status = status
#         self.color = self._get_color()
    
#     def update(self, dt):
#         # print(f"Vehicle {self.vehicle_id}: {len(self._orders)} orders, {len(self._routes)} routes, status={self.status}, position=({self.x():.5f}, {self.y():.5f}))")
#         # if self._routes:
#         if self._orders and self._orders[0] is not None or self.active_route:
#             # DO NOT override status here - let simulation manage it
#             current = self.active_route
#             # segment, speed = self._routes[0][self.segment_index]
#             segment, speed = current[self.segment_index]
#             self.segment_progress += speed / 11000 * dt
#             self.segment_progress = min(self.segment_progress, segment.length)
#             position = segment.interpolate(self.segment_progress)
#             self._x = position.x
#             self._y = position.y
#             if self.segment_progress >= segment.length:
#                 self.segment_index += 1
#                 self.segment_progress = 0
#                 # if self.segment_index >= len(self._routes[0]):
#                 if self.segment_index >= len(current):
#                     self._route_complete = True
#                     self.segment_index = 0
#         # if self._route_complete and self._orders and self._orders[0] is not None:
#         if self._route_complete and self.current_order is not None:
#             # If we just completed a route, update order status
#             order = self.current_order
#             self.current_order = None
#             if order.status == OrderStatus.ASSIGNED:
#                 order.pick_up()
#             elif order.status == OrderStatus.PICKED_UP:
#                 order.drop_off()
#             # Clear the completed route and order
#             self.active_route = order.route
#             # self._status = VehicleStatus.IN_ROUTE
#             self.segment_index = 0
#             self.segment_progress = 0
#             self._route_complete = False

#     def _get_color(self):
#         if self.status == VehicleStatus.IDLE:
#             return 'green'
#         elif self.status == VehicleStatus.TO_PICKUP:
#             return 'yellow'
#         elif self.status == VehicleStatus.IN_ROUTE:
#             return 'blue'
#         elif self.status == VehicleStatus.OFFLINE:
#             return 'red'
        
#     def assign_order(self, order, pickup_route):
#         # pickup_route = order.route  # route is pickup -> dropoff
#         # self.assign_route(pickup_route, order=order)
#         self.current_order = order
#         self.active_route = pickup_route
        
#         # 2. Lock the vehicle's state
#         self.set_status(VehicleStatus.TO_PICKUP)
        
#         # 3. Update the order's state
#         self.current_order.set_status(OrderStatus.ASSIGNED)
#         self.current_order.assign_vehicle(self)
    
#     def assign_route(self, route: list, order=None):
#         self._routes.append(route)
#         self._orders.append(order)
#         # self.status = VehicleStatus.IN_ROUTE
#         # self.color = self._get_color()
#         # Only reset progress if this is the first route
#         if len(self._routes) == 1:
#             self.segment_index = 0
#             self.segment_progress = 0
#             self.position = self._routes[0][0][0].interpolate(0)
        
    
#     def __str__(self):
#         return f"Vehicle({self.vehicle_id}, ({self.x}, {self.y}), capacity={self.capacity}, status={self.status})"
    