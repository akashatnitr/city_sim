"""
Traffic system module for AI City Simulator.
Manages traffic flow and congestion.
"""
import random
import math


class TrafficSystem:
    """Manages traffic flow and congestion in the city."""
    
    def __init__(self, simulation, config):
        """
        Initialize the traffic system.
        
        Args:
            simulation: The simulation instance
            config (dict): Configuration dictionary for traffic
        """
        self.simulation = simulation
        self.config = config
        self.enable_traffic = config.get('enable_traffic', True)
        self.congestion_factor = config.get('congestion_factor', 1.0)
        
        # Traffic jams
        self.traffic_jams = []
        
        # Traffic statistics
        self.stats = {
            'total_jams': 0,
            'current_jams': 0,
            'average_congestion': 0.0,
        }
        
        # Vehicles (not controlled by agents)
        self.vehicles = []
        
        # Bus system
        self.buses = []
        self._initialize_buses()
    
    def _initialize_buses(self):
        """Initialize the bus system."""
        # Create buses for each route
        for route in self.simulation.city.road_network.bus_routes:
            # Create a bus for this route
            bus = {
                'id': f"bus_{route['id']}",
                'route': route,
                'current_node_index': 0,
                'x': route['nodes'][0][0],
                'y': route['nodes'][0][1],
                'passengers': [],
                'capacity': 20,
                'speed': 3.0,
                'next_stop_index': 0,
                'stopped': False,
                'stop_duration': 0,
                'max_stop_duration': 50,  # Ticks to wait at a stop
            }
            
            self.buses.append(bus)
    
    def update(self):
        """Update the traffic system."""
        if not self.enable_traffic:
            return
        
        # Update traffic jams
        self._update_traffic_jams()
        
        # Generate new traffic jams
        self._generate_traffic_jams()
        
        # Update vehicles
        self._update_vehicles()
        
        # Update buses
        self._update_buses()
        
        # Update statistics
        self._update_statistics()
    
    def _update_traffic_jams(self):
        """Update traffic jams."""
        # Remove expired traffic jams
        self.traffic_jams = [jam for jam in self.traffic_jams if not jam['expired']]
        
        # Update each traffic jam
        for jam in self.traffic_jams:
            # Increment duration
            jam['duration'] += 1
            
            # Check if jam has expired
            if jam['duration'] >= jam['max_duration']:
                jam['expired'] = True
                continue
            
            # Update congestion
            jam['congestion'] = max(0.0, jam['congestion'] - 0.01)
            
            # Update road network traffic
            edge = (jam['start_node'], jam['end_node'])
            self.simulation.city.road_network.update_traffic(edge, -0.01)
    
    def _generate_traffic_jams(self):
        """Generate new traffic jams."""
        # Get the current traffic jam probability
        jam_probability = self._calculate_jam_probability()
        
        # Check if a traffic jam occurs
        if random.random() < jam_probability:
            self._create_traffic_jam()
    
    def _calculate_jam_probability(self):
        """
        Calculate the current traffic jam probability based on various factors.
        
        Returns:
            float: Current traffic jam probability
        """
        # Base probability
        probability = 0.001 * self.congestion_factor
        
        # Adjust for time of day
        day_phase = self.simulation.get_day_phase()
        if day_phase == 'morning' or day_phase == 'evening':
            probability *= 3.0  # More traffic during rush hour
        elif day_phase == 'night':
            probability *= 0.2  # Less traffic at night
        
        # Adjust for weather
        weather_effect = self.simulation.weather_system.get_weather_effect('traffic_modifier')
        probability *= weather_effect
        
        # Adjust for number of agents
        agent_count = self.simulation.agent_manager.get_agent_count()
        probability *= 1.0 + min(1.0, agent_count / 100)
        
        return probability * self.simulation.speed
    
    def _create_traffic_jam(self):
        """Create a new traffic jam."""
        # Choose a road segment
        road_network = self.simulation.city.road_network
        edges = list(road_network.graph.edges())
        
        if not edges:
            return
        
        edge = random.choice(edges)
        start_node, end_node = edge
        
        # Calculate the midpoint of the edge
        x = (start_node[0] + end_node[0]) / 2
        y = (start_node[1] + end_node[1]) / 2
        
        # Create the traffic jam
        jam = {
            'start_node': start_node,
            'end_node': end_node,
            'x': x,
            'y': y,
            'congestion': random.uniform(0.5, 1.0),
            'duration': 0,
            'max_duration': random.randint(100, 500),  # Traffic jams last a while
            'expired': False,
        }
        
        # Add to traffic jams
        self.traffic_jams.append(jam)
        
        # Update road network traffic
        road_network.update_traffic(edge, jam['congestion'])
        
        # Update statistics
        self.stats['total_jams'] += 1
        
        print(f"Traffic jam occurred at ({x:.0f}, {y:.0f}), congestion: {jam['congestion']:.2f}")
    
    def _update_vehicles(self):
        """Update autonomous vehicles."""
        # Remove vehicles that have reached their destination
        self.vehicles = [v for v in self.vehicles if not v['reached_destination']]
        
        # Update each vehicle
        for vehicle in self.vehicles:
            # If the vehicle has a path, follow it
            if vehicle['path']:
                # Get the next point in the path
                next_x, next_y = vehicle['path'][0]
                
                # Calculate direction and distance to the next point
                dx = next_x - vehicle['x']
                dy = next_y - vehicle['y']
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Calculate speed based on traffic
                base_speed = vehicle['speed']
                current_edge = self._find_current_edge(vehicle['x'], vehicle['y'])
                
                if current_edge:
                    traffic = self.simulation.city.road_network.get_traffic_level(current_edge)
                    speed = base_speed * (1.0 - traffic * 0.8)  # Traffic reduces speed
                else:
                    speed = base_speed
                
                if distance <= speed:
                    # We've reached this point, move to the next one
                    vehicle['x'] = next_x
                    vehicle['y'] = next_y
                    vehicle['path'].pop(0)
                    
                    # Check if we've reached the destination
                    if not vehicle['path']:
                        vehicle['reached_destination'] = True
                else:
                    # Move towards the next point
                    direction_x = dx / distance
                    direction_y = dy / distance
                    
                    vehicle['x'] += direction_x * speed
                    vehicle['y'] += direction_y * speed
            else:
                # No path, mark as reached destination
                vehicle['reached_destination'] = True
        
        # Generate new vehicles
        if len(self.vehicles) < 50 and random.random() < 0.05 * self.simulation.speed:
            self._create_vehicle()
    
    def _create_vehicle(self):
        """Create a new autonomous vehicle."""
        # Choose a random start and end location
        city = self.simulation.city
        start_location = random.choice(city.get_all_locations())
        end_location = random.choice(city.get_all_locations())
        
        # Don't go to the same location
        while end_location == start_location:
            end_location = random.choice(city.get_all_locations())
        
        # Find a path
        path = city.road_network.find_path(start_location.x, start_location.y, 
                                          end_location.x, end_location.y)
        
        if not path:
            return
        
        # Create the vehicle
        vehicle = {
            'id': f"vehicle_{len(self.vehicles)}",
            'x': start_location.x,
            'y': start_location.y,
            'path': path,
            'speed': random.uniform(2.0, 4.0),
            'reached_destination': False,
        }
        
        # Add to vehicles
        self.vehicles.append(vehicle)
    
    def _update_buses(self):
        """Update buses."""
        # Update each bus
        for bus in self.buses:
            if bus['stopped']:
                # Bus is at a stop
                bus['stop_duration'] += 1
                
                if bus['stop_duration'] >= bus['max_stop_duration']:
                    # Time to leave
                    bus['stopped'] = False
                    bus['stop_duration'] = 0
                    bus['next_stop_index'] = (bus['next_stop_index'] + 1) % len(bus['route']['stops'])
            else:
                # Bus is moving
                route = bus['route']
                nodes = route['nodes']
                current_index = bus['current_node_index']
                
                # Get the current and next node
                current_node = nodes[current_index]
                next_index = (current_index + 1) % len(nodes)
                next_node = nodes[next_index]
                
                # Calculate direction and distance to the next node
                dx = next_node[0] - bus['x']
                dy = next_node[1] - bus['y']
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Calculate speed based on traffic
                base_speed = bus['speed']
                current_edge = (current_node, next_node)
                traffic = self.simulation.city.road_network.get_traffic_level(current_edge)
                speed = base_speed * (1.0 - traffic * 0.8)  # Traffic reduces speed
                
                if distance <= speed:
                    # We've reached this node, move to the next one
                    bus['x'] = next_node[0]
                    bus['y'] = next_node[1]
                    bus['current_node_index'] = next_index
                    
                    # Check if this is a bus stop
                    stops = route['stops']
                    if bus['next_stop_index'] < len(stops):
                        next_stop = stops[bus['next_stop_index']]
                        
                        if next_stop['x'] == next_node[0] and next_stop['y'] == next_node[1]:
                            # We've reached a stop
                            bus['stopped'] = True
                else:
                    # Move towards the next node
                    direction_x = dx / distance
                    direction_y = dy / distance
                    
                    bus['x'] += direction_x * speed
                    bus['y'] += direction_y * speed
    
    def _find_current_edge(self, x, y):
        """
        Find the edge that a position is on or closest to.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            
        Returns:
            tuple or None: The edge, or None if no edge is close enough
        """
        road_network = self.simulation.city.road_network
        edges = list(road_network.graph.edges())
        
        closest_edge = None
        closest_distance = float('inf')
        
        for edge in edges:
            start_node, end_node = edge
            
            # Calculate the distance from the point to the line segment
            distance = self._point_to_line_distance(x, y, start_node[0], start_node[1], 
                                                  end_node[0], end_node[1])
            
            if distance < closest_distance:
                closest_distance = distance
                closest_edge = edge
        
        # Only return the edge if it's close enough
        if closest_distance <= 20:
            return closest_edge
        
        return None
    
    def _point_to_line_distance(self, x, y, x1, y1, x2, y2):
        """
        Calculate the distance from a point to a line segment.
        
        Args:
            x, y: Point coordinates
            x1, y1: Start of line segment
            x2, y2: End of line segment
            
        Returns:
            float: Distance from point to line segment
        """
        # Calculate the squared length of the line segment
        line_length_squared = (x2 - x1) ** 2 + (y2 - y1) ** 2
        
        if line_length_squared == 0:
            # The line segment is actually a point
            return math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        
        # Calculate the projection of the point onto the line
        t = max(0, min(1, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / line_length_squared))
        
        # Calculate the closest point on the line segment
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
        # Calculate the distance to the closest point
        return math.sqrt((x - closest_x) ** 2 + (y - closest_y) ** 2)
    
    def _update_statistics(self):
        """Update traffic statistics."""
        # Count current jams
        self.stats['current_jams'] = len(self.traffic_jams)
        
        # Calculate average congestion
        if self.traffic_jams:
            total_congestion = sum(jam['congestion'] for jam in self.traffic_jams)
            self.stats['average_congestion'] = total_congestion / len(self.traffic_jams)
        else:
            self.stats['average_congestion'] = 0.0
    
    def get_traffic_jams(self):
        """
        Get all traffic jams.
        
        Returns:
            list: List of traffic jams
        """
        return self.traffic_jams
    
    def get_vehicles(self):
        """
        Get all vehicles.
        
        Returns:
            list: List of vehicles
        """
        return self.vehicles
    
    def get_buses(self):
        """
        Get all buses.
        
        Returns:
            list: List of buses
        """
        return self.buses
    
    def get_traffic_heatmap(self):
        """
        Get a traffic heatmap.
        
        Returns:
            list: List of (x, y, intensity) tuples for the heatmap
        """
        heatmap = []
        
        # Add traffic jams to the heatmap
        for jam in self.traffic_jams:
            heatmap.append((jam['x'], jam['y'], jam['congestion']))
        
        # Add general traffic from the road network
        road_network = self.simulation.city.road_network
        for edge, traffic in road_network.traffic.items():
            if traffic > 0.2:  # Only include edges with significant traffic
                start_node, end_node = edge
                x = (start_node[0] + end_node[0]) / 2
                y = (start_node[1] + end_node[1]) / 2
                heatmap.append((x, y, traffic))
        
        return heatmap
