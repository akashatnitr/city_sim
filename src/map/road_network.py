"""
Road network module for AI City Simulator.
Manages the city's roads, intersections, and pathfinding.
"""
import random
import networkx as nx
import numpy as np
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class RoadNetwork:
    """Represents the road network of the city."""
    
    def __init__(self, width, height):
        """
        Initialize the road network.
        
        Args:
            width (int): Width of the city
            height (int): Height of the city
        """
        self.width = width
        self.height = height
        
        # Graph representation of the road network
        self.graph = nx.Graph()
        
        # Grid representation for pathfinding
        self.grid_size = 10  # Each grid cell is 10x10 units
        self.grid_width = width // self.grid_size
        self.grid_height = height // self.grid_size
        self.grid_matrix = np.ones((self.grid_height, self.grid_width), dtype=int)
        
        # Traffic information
        self.traffic = {}  # Edge -> traffic level (0-1)
        
        # Bus routes
        self.bus_routes = []
        self.bus_stops = []
    
    def generate_grid_roads(self, grid_size=200, main_road_width=10):
        """
        Generate a grid-based road network.
        
        Args:
            grid_size (int): Size of the grid cells
            main_road_width (int): Width of main roads
        """
        # Create a grid of roads
        for x in range(0, self.width, grid_size):
            # Vertical road
            for y in range(0, self.height - 1, grid_size // 4):
                self.graph.add_edge((x, y), (x, min(y + grid_size // 4, self.height - 1)))
                
                # Mark road in grid matrix
                grid_x = x // self.grid_size
                for grid_y in range(y // self.grid_size, min((y + grid_size // 4) // self.grid_size + 1, self.grid_height)):
                    if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                        self.grid_matrix[grid_y, grid_x] = 0  # 0 means walkable
        
        for y in range(0, self.height, grid_size):
            # Horizontal road
            for x in range(0, self.width - 1, grid_size // 4):
                self.graph.add_edge((x, y), (min(x + grid_size // 4, self.width - 1), y))
                
                # Mark road in grid matrix
                grid_y = y // self.grid_size
                for grid_x in range(x // self.grid_size, min((x + grid_size // 4) // self.grid_size + 1, self.grid_width)):
                    if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                        self.grid_matrix[grid_y, grid_x] = 0  # 0 means walkable
        
        # Add some diagonal roads for variety
        for _ in range(5):
            # Choose two random points on the grid
            x1, y1 = random.randint(0, self.width // grid_size) * grid_size, random.randint(0, self.height // grid_size) * grid_size
            x2, y2 = random.randint(0, self.width // grid_size) * grid_size, random.randint(0, self.height // grid_size) * grid_size
            
            # Create a diagonal road between them
            steps = max(abs(x2 - x1), abs(y2 - y1)) // (grid_size // 4)
            if steps > 0:
                dx = (x2 - x1) / steps
                dy = (y2 - y1) / steps
                
                for i in range(steps):
                    x = int(x1 + i * dx)
                    y = int(y1 + i * dy)
                    next_x = int(x1 + (i + 1) * dx)
                    next_y = int(y1 + (i + 1) * dy)
                    
                    self.graph.add_edge((x, y), (next_x, next_y))
                    
                    # Mark road in grid matrix
                    for j in range(10):  # Add multiple points along the line
                        interp_x = int(x + j * (next_x - x) / 10)
                        interp_y = int(y + j * (next_y - y) / 10)
                        
                        grid_x = interp_x // self.grid_size
                        grid_y = interp_y // self.grid_size
                        
                        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                            self.grid_matrix[grid_y, grid_x] = 0
        
        # Initialize traffic for each edge
        for edge in self.graph.edges():
            self.traffic[edge] = 0.0
        
        # Generate bus routes
        self._generate_bus_routes(5)  # Create 5 bus routes
    
    def _generate_bus_routes(self, num_routes):
        """
        Generate bus routes throughout the city.
        
        Args:
            num_routes (int): Number of bus routes to generate
        """
        for route_id in range(num_routes):
            # Choose a random starting point on the road network
            start_node = random.choice(list(self.graph.nodes()))
            
            # Create a route with 10-15 stops
            route = [start_node]
            current_node = start_node
            
            for _ in range(random.randint(10, 15)):
                # Get neighbors of current node
                neighbors = list(self.graph.neighbors(current_node))
                
                # If no neighbors, break
                if not neighbors:
                    break
                
                # Choose a random neighbor that's not already in the route
                valid_neighbors = [n for n in neighbors if n not in route]
                
                # If no valid neighbors, try any neighbor
                if not valid_neighbors:
                    valid_neighbors = neighbors
                
                # Choose next node
                next_node = random.choice(valid_neighbors)
                route.append(next_node)
                current_node = next_node
            
            # Add bus stops along the route
            stops = []
            for i in range(len(route)):
                if i % 2 == 0:  # Every other node becomes a bus stop
                    x, y = route[i]
                    stops.append({
                        'id': f"bus_stop_{route_id}_{i}",
                        'name': f"Bus Stop {route_id}-{i}",
                        'x': x,
                        'y': y,
                        'route_id': route_id
                    })
            
            # Add the route and stops
            self.bus_routes.append({
                'id': route_id,
                'name': f"Route {route_id}",
                'color': (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                'nodes': route,
                'stops': stops
            })
            
            self.bus_stops.extend(stops)
    
    def connect_location_to_nearest_road(self, location):
        """
        Connect a location to the nearest road.
        
        Args:
            location: Location to connect
            
        Returns:
            tuple: The road node that the location is connected to
        """
        # Find the nearest node in the road network
        nearest_node = min(self.graph.nodes(), 
                          key=lambda node: ((node[0] - location.x) ** 2 + (node[1] - location.y) ** 2) ** 0.5)
        
        # Add an edge from the location to the nearest node
        self.graph.add_edge((location.x, location.y), nearest_node)
        
        # Update the grid matrix
        loc_grid_x = int(location.x) // self.grid_size
        loc_grid_y = int(location.y) // self.grid_size
        
        if 0 <= loc_grid_x < self.grid_width and 0 <= loc_grid_y < self.grid_height:
            self.grid_matrix[loc_grid_y, loc_grid_x] = 0
        
        # Draw a path from the location to the nearest node in the grid
        node_grid_x = int(nearest_node[0]) // self.grid_size
        node_grid_y = int(nearest_node[1]) // self.grid_size
        
        # Simple line drawing algorithm
        if loc_grid_x != node_grid_x or loc_grid_y != node_grid_y:
            steps = max(abs(node_grid_x - loc_grid_x), abs(node_grid_y - loc_grid_y))
            if steps > 0:
                dx = (node_grid_x - loc_grid_x) / steps
                dy = (node_grid_y - loc_grid_y) / steps
                
                for i in range(steps + 1):
                    x = int(loc_grid_x + i * dx)
                    y = int(loc_grid_y + i * dy)
                    
                    if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                        self.grid_matrix[y, x] = 0
        
        return nearest_node
    
    def find_path(self, start_x, start_y, end_x, end_y):
        """
        Find a path from start to end using A* pathfinding.
        
        Args:
            start_x (float): Starting X coordinate
            start_y (float): Starting Y coordinate
            end_x (float): Ending X coordinate
            end_y (float): Ending Y coordinate
            
        Returns:
            list: List of (x, y) coordinates forming the path
        """
        # Convert to grid coordinates
        start_grid_x = int(start_x) // self.grid_size
        start_grid_y = int(start_y) // self.grid_size
        end_grid_x = int(end_x) // self.grid_size
        end_grid_y = int(end_y) // self.grid_size
        
        # Ensure coordinates are within bounds
        start_grid_x = max(0, min(start_grid_x, self.grid_width - 1))
        start_grid_y = max(0, min(start_grid_y, self.grid_height - 1))
        end_grid_x = max(0, min(end_grid_x, self.grid_width - 1))
        end_grid_y = max(0, min(end_grid_y, self.grid_height - 1))
        
        # Create a grid from the matrix
        grid = Grid(matrix=self.grid_matrix)
        
        # Create start and end nodes
        start = grid.node(start_grid_x, start_grid_y)
        end = grid.node(end_grid_x, end_grid_y)
        
        # Create a finder with A*
        finder = AStarFinder()
        
        # Find the path
        path, _ = finder.find_path(start, end, grid)
        
        # Convert back to world coordinates
        world_path = [(node.x * self.grid_size + self.grid_size // 2, 
                       node.y * self.grid_size + self.grid_size // 2) for node in path]
        
        return world_path
    
    def update_traffic(self, edge, amount):
        """
        Update the traffic level on an edge.
        
        Args:
            edge: The edge to update
            amount (float): Amount to change traffic by (-1 to 1)
        """
        if edge in self.traffic:
            self.traffic[edge] = max(0, min(1, self.traffic[edge] + amount))
    
    def get_traffic_level(self, edge):
        """
        Get the traffic level on an edge.
        
        Args:
            edge: The edge to check
            
        Returns:
            float: Traffic level from 0 (none) to 1 (gridlock)
        """
        return self.traffic.get(edge, 0)
    
    def get_nearest_bus_stop(self, x, y):
        """
        Find the nearest bus stop to the given coordinates.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            
        Returns:
            dict: The nearest bus stop
        """
        if not self.bus_stops:
            return None
        
        return min(self.bus_stops, 
                  key=lambda stop: ((stop['x'] - x) ** 2 + (stop['y'] - y) ** 2) ** 0.5)
    
    def update(self):
        """Update the road network state."""
        # Gradually reduce traffic on all edges
        for edge in self.traffic:
            self.traffic[edge] = max(0, self.traffic[edge] - 0.01)
        
        # Randomly increase traffic on some edges to simulate traffic patterns
        for _ in range(10):
            edge = random.choice(list(self.graph.edges()))
            self.update_traffic(edge, random.uniform(0, 0.1))
