class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
    
    
    def __str__(self):
        return f"Node({self.x}, {self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y