import enum

class VehicleStatus(enum.Enum):
    IDLE = 1
    TO_PICKUP = 2
    IN_ROUTE = 3
    OFFLINE = 4