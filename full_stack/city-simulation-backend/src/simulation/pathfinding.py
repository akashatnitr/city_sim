import math
import heapq
from typing import List, Tuple, Dict, Optional

class PathfindingSystem:
    """Handles pathfinding for agents in the city"""
    
    def __init__(self, simulation_engine):
        self.simulation_engine = simulation_engine
        self.graph_cache = {}
        self.path_cache = {}
    
    def find_path(self, start_location_id: int, end_location_id: int, 
                  transport_mode: str = 'walking') -> Optional[List[Dict]]:
        """Find optimal path between two locations"""
        
        # Check cache first
        cache_key = (start_location_id, end_location_id, transport_mode)
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]
        
        # Get locations
        locations = self.simulation_engine.locations
        roads = self.simulation_engine.roads
        
        if start_location_id not in locations or end_location_id not in locations:
            return None
        
        # Build graph for pathfinding
        graph = self._build_graph(locations, roads, transport_mode)
        
        # Use A* algorithm
        path = self._a_star(graph, start_location_id, end_location_id, locations)
        
        if path:
            # Convert to detailed path with waypoints
            detailed_path = self._create_detailed_path(path, locations, roads, transport_mode)
            self.path_cache[cache_key] = detailed_path
            return detailed_path
        
        return None
    
    def _build_graph(self, locations: Dict, roads: Dict, transport_mode: str) -> Dict:
        """Build graph representation for pathfinding"""
        graph = {}
        
        # Initialize graph with all locations
        for location_id in locations:
            graph[location_id] = []
        
        # Add edges based on roads
        for road_id, road_data in roads.items():
            from_id = road_data['from_location_id']
            to_id = road_data['to_location_id']
            
            if from_id in graph and to_id in graph:
                # Calculate cost based on transport mode and road conditions
                cost = self._calculate_road_cost(road_data, transport_mode)
                
                if cost < float('inf'):  # Road is passable
                    graph[from_id].append((to_id, cost))
                    # Add reverse direction for most roads
                    if road_data.get('road_type') != 'one_way':
                        graph[to_id].append((from_id, cost))
        
        return graph
    
    def _calculate_road_cost(self, road_data: Dict, transport_mode: str) -> float:
        """Calculate cost of traversing a road"""
        if road_data.get('is_blocked', False):
            return float('inf')
        
        distance = road_data.get('distance', 1.0)
        traffic_multiplier = road_data.get('current_traffic', 1.0)
        
        # Base speed by transport mode
        base_speeds = {
            'walking': 5.0,  # km/h
            'cycling': 15.0,
            'car': min(road_data.get('speed_limit', 50.0), 60.0),
            'bus': min(road_data.get('speed_limit', 50.0) * 0.8, 40.0),
            'metro': 80.0
        }
        
        speed = base_speeds.get(transport_mode, 5.0)
        
        # Apply traffic effects (mainly for cars and buses)
        if transport_mode in ['car', 'bus']:
            speed /= traffic_multiplier
        
        # Apply weather effects
        weather_modifier = self.simulation_engine.weather_system.get_movement_modifier()
        speed *= weather_modifier
        
        # Calculate time cost (in minutes)
        time_cost = (distance / speed) * 60
        
        return time_cost
    
    def _a_star(self, graph: Dict, start: int, goal: int, locations: Dict) -> Optional[List[int]]:
        """A* pathfinding algorithm"""
        
        def heuristic(location_id: int) -> float:
            """Euclidean distance heuristic"""
            if location_id not in locations or goal not in locations:
                return 0
            
            loc1 = locations[location_id]
            loc2 = locations[goal]
            
            dx = loc1['x'] - loc2['x']
            dy = loc1['y'] - loc2['y']
            
            return math.sqrt(dx * dx + dy * dy)
        
        # Priority queue: (f_score, location_id)
        open_set = [(0, start)]
        came_from = {}
        
        g_score = {start: 0}
        f_score = {start: heuristic(start)}
        
        while open_set:
            current_f, current = heapq.heappop(open_set)
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            if current not in graph:
                continue
            
            for neighbor, cost in graph[current]:
                tentative_g = g_score[current] + cost
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor)
                    
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # No path found
    
    def _create_detailed_path(self, path: List[int], locations: Dict, 
                            roads: Dict, transport_mode: str) -> List[Dict]:
        """Create detailed path with waypoints and instructions"""
        detailed_path = []
        
        for i in range(len(path)):
            location_id = path[i]
            location = locations[location_id]
            
            waypoint = {
                'location_id': location_id,
                'x': location['x'],
                'y': location['y'],
                'name': location['name'],
                'type': location['type']
            }
            
            if i < len(path) - 1:
                next_location_id = path[i + 1]
                # Find road between current and next location
                road = self._find_road_between(location_id, next_location_id, roads)
                if road:
                    waypoint['road_id'] = road['id']
                    waypoint['distance_to_next'] = road['distance']
                    waypoint['travel_time'] = self._calculate_road_cost(road, transport_mode)
            
            detailed_path.append(waypoint)
        
        return detailed_path
    
    def _find_road_between(self, from_id: int, to_id: int, roads: Dict) -> Optional[Dict]:
        """Find road connecting two locations"""
        for road_data in roads.values():
            if ((road_data['from_location_id'] == from_id and road_data['to_location_id'] == to_id) or
                (road_data['from_location_id'] == to_id and road_data['to_location_id'] == from_id)):
                return road_data
        return None
    
    def get_nearby_locations(self, x: float, y: float, radius: float = 1.0) -> List[Dict]:
        """Get locations within a certain radius"""
        nearby = []
        locations = self.simulation_engine.locations
        
        for location_id, location_data in locations.items():
            dx = location_data['x'] - x
            dy = location_data['y'] - y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= radius:
                nearby.append({
                    'location_id': location_id,
                    'distance': distance,
                    **location_data
                })
        
        # Sort by distance
        nearby.sort(key=lambda x: x['distance'])
        return nearby
    
    def calculate_travel_time(self, start_location_id: int, end_location_id: int,
                            transport_mode: str = 'walking') -> float:
        """Calculate total travel time between two locations"""
        path = self.find_path(start_location_id, end_location_id, transport_mode)
        
        if not path:
            return float('inf')
        
        total_time = 0
        for waypoint in path:
            if 'travel_time' in waypoint:
                total_time += waypoint['travel_time']
        
        return total_time
    
    def clear_cache(self):
        """Clear pathfinding cache (useful when roads change)"""
        self.path_cache.clear()
        self.graph_cache.clear()
    
    def update_traffic(self, road_id: int, traffic_multiplier: float):
        """Update traffic conditions for a road"""
        if road_id in self.simulation_engine.roads:
            self.simulation_engine.roads[road_id]['current_traffic'] = traffic_multiplier
            # Clear cache as traffic conditions changed
            self.clear_cache()

