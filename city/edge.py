class Edge:
    def __init__(self, start_node, end_node, weight):
        self.start_node = start_node
        self.end_node = end_node
        self.weight = weight
    
    def __str__(self):
        return f"Edge({self.start_node} -> {self.end_node}, weight={self.weight})"