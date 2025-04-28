"""
City module for AI City Simulator.
Manages city layout, locations, and infrastructure.
"""
import random
import networkx as nx
from datetime import datetime

from src.map.location import Location
from src.map.road_network import RoadNetwork


class City:
    """Represents the city with all its locations and infrastructure."""
    
    def __init__(self, config):
        """
        Initialize the city with the given configuration.
        
        Args:
            config (dict): Configuration dictionary for the city
        """
        self.config = config
        self.name = config.get('name', 'AI City')
        self.width = config.get('width', 2000)
        self.height = config.get('height', 2000)
        
        # Initialize locations by category
        self.locations = {
            'residential': [],  # Homes, apartments, etc.
            'commercial': [],   # Stores, restaurants, etc.
            'educational': [],  # Schools, colleges, etc.
            'transportation': [], # Airport, bus stops, etc.
            'recreation': [],   # Parks, gyms, etc.
            'service': [],      # Police, hospitals, etc.
        }
        
        # Initialize road network
        self.road_network = RoadNetwork(self.width, self.height)
        
        # Generate initial city layout
        self._generate_city_layout()
        
        # Track city statistics
        self.stats = {
            'population': 0,
            'crime_rate': 0.0,
            'happiness': 50.0,
            'economy': 50.0,
            'traffic_congestion': 0.0,
        }
    
    def _generate_city_layout(self):
        """Generate the initial city layout with roads and locations."""
        # Generate main roads
        self.road_network.generate_grid_roads(
            grid_size=self.config.get('grid_size', 200),
            main_road_width=self.config.get('main_road_width', 10)
        )
        
        # Generate residential areas
        self._generate_locations('residential', 
                                self.config.get('residential_count', 100),
                                ['House', 'Apartment', 'Condo', 'Senior Living'])
        
        # Generate commercial areas
        self._generate_locations('commercial', 
                                self.config.get('commercial_count', 50),
                                ['Grocery Store', 'Restaurant', 'Coffee Shop', 'Bar', 'Gym', 'Shopping Mall'])
        
        # Generate educational institutions
        self._generate_locations('educational', 
                                self.config.get('educational_count', 10),
                                ['Elementary School', 'High School', 'College', 'Library'])
        
        # Generate transportation hubs
        self._generate_locations('transportation', 
                                self.config.get('transportation_count', 30),
                                ['Bus Stop', 'Train Station', 'Airport'])
        
        # Generate recreational areas
        self._generate_locations('recreation', 
                                self.config.get('recreation_count', 20),
                                ['Park', 'Movie Theater', 'Sports Stadium', 'Museum'])
        
        # Generate service buildings
        self._generate_locations('service', 
                                self.config.get('service_count', 10),
                                ['Police Station', 'Hospital', 'Fire Station', 'City Hall'])
        
        # Connect all locations to the road network
        for category in self.locations:
            for location in self.locations[category]:
                self.road_network.connect_location_to_nearest_road(location)
    
    def _generate_locations(self, category, count, types):
        """
        Generate locations of a specific category.
        
        Args:
            category (str): Category of locations to generate
            count (int): Number of locations to generate
            types (list): List of location types to choose from
        """
        for _ in range(count):
            # Choose a random type for this location
            loc_type = random.choice(types)
            
            # Generate a name based on the type
            if loc_type == 'House':
                name = f"{random.choice(['Pine', 'Oak', 'Maple', 'Cedar', 'Elm'])} {random.choice(['St', 'Ave', 'Blvd'])} {random.randint(100, 999)}"
            elif loc_type == 'Apartment':
                name = f"{random.choice(['Sunset', 'Riverside', 'Mountain View', 'Lakeside', 'Urban'])} Apartments"
            elif loc_type == 'Restaurant':
                name = f"{random.choice(['Tasty', 'Delicious', 'Gourmet', 'Fine', 'Quick'])} {random.choice(['Eats', 'Bites', 'Cuisine', 'Dining', 'Food'])}"
            elif loc_type == 'Grocery Store':
                name = f"{random.choice(['Fresh', 'Super', 'Value', 'Quality', 'City'])} {random.choice(['Market', 'Grocers', 'Foods', 'Mart'])}"
            else:
                name = f"{self.name} {loc_type}"
            
            # Find a position for this location
            # For simplicity, we'll place it randomly, but in a real implementation
            # we'd want to cluster similar locations and follow zoning rules
            x = random.randint(50, self.width - 50)
            y = random.randint(50, self.height - 50)
            
            # Create the location
            location = Location(
                name=name,
                location_type=loc_type,
                category=category,
                x=x,
                y=y,
                capacity=random.randint(5, 50)
            )
            
            # Add to the appropriate category
            self.locations[category].append(location)
    
    def get_all_locations(self):
        """Get all locations in the city."""
        all_locations = []
        for category in self.locations:
            all_locations.extend(self.locations[category])
        return all_locations
    
    def get_locations_by_category(self, category):
        """Get all locations in a specific category."""
        return self.locations.get(category, [])
    
    def get_locations_by_type(self, location_type):
        """Get all locations of a specific type."""
        return [loc for category in self.locations.values() 
                for loc in category if loc.location_type == location_type]
    
    def get_nearest_location(self, x, y, category=None, location_type=None):
        """
        Find the nearest location to the given coordinates.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            category (str, optional): Filter by category
            location_type (str, optional): Filter by location type
            
        Returns:
            Location: The nearest location matching the criteria
        """
        locations = self.get_all_locations()
        
        if category:
            locations = [loc for loc in locations if loc.category == category]
        
        if location_type:
            locations = [loc for loc in locations if loc.location_type == location_type]
        
        if not locations:
            return None
        
        return min(locations, key=lambda loc: ((loc.x - x) ** 2 + (loc.y - y) ** 2) ** 0.5)
    
    def update(self, current_time):
        """
        Update the city state based on the current simulation time.
        
        Args:
            current_time (datetime): Current simulation time
        """
        # Update each location
        for category in self.locations:
            for location in self.locations[category]:
                location.update(current_time)
        
        # Update road network
        self.road_network.update()
    
    def grow(self):
        """Grow the city by adding new locations."""
        # Determine which category to grow
        category = random.choice(list(self.locations.keys()))
        
        # Get existing types for this category
        existing_types = set(loc.location_type for loc in self.locations[category])
        
        # Define possible types for each category
        category_types = {
            'residential': ['House', 'Apartment', 'Condo', 'Senior Living'],
            'commercial': ['Grocery Store', 'Restaurant', 'Coffee Shop', 'Bar', 'Gym', 'Shopping Mall'],
            'educational': ['Elementary School', 'High School', 'College', 'Library'],
            'transportation': ['Bus Stop', 'Train Station'],
            'recreation': ['Park', 'Movie Theater', 'Sports Stadium', 'Museum'],
            'service': ['Police Station', 'Hospital', 'Fire Station']
        }
        
        # Choose a type for the new location
        possible_types = category_types.get(category, ['Building'])
        loc_type = random.choice(possible_types)
        
        # Generate a name
        if loc_type == 'House':
            name = f"{random.choice(['Pine', 'Oak', 'Maple', 'Cedar', 'Elm'])} {random.choice(['St', 'Ave', 'Blvd'])} {random.randint(100, 999)}"
        elif loc_type == 'Apartment':
            name = f"{random.choice(['Sunset', 'Riverside', 'Mountain View', 'Lakeside', 'Urban'])} Apartments"
        elif loc_type == 'Restaurant':
            name = f"{random.choice(['Tasty', 'Delicious', 'Gourmet', 'Fine', 'Quick'])} {random.choice(['Eats', 'Bites', 'Cuisine', 'Dining', 'Food'])}"
        elif loc_type == 'Grocery Store':
            name = f"{random.choice(['Fresh', 'Super', 'Value', 'Quality', 'City'])} {random.choice(['Market', 'Grocers', 'Foods', 'Mart'])}"
        else:
            name = f"New {self.name} {loc_type}"
        
        # Find a position for this location
        x = random.randint(50, self.width - 50)
        y = random.randint(50, self.height - 50)
        
        # Create the location
        location = Location(
            name=name,
            location_type=loc_type,
            category=category,
            x=x,
            y=y,
            capacity=random.randint(5, 50)
        )
        
        # Add to the appropriate category
        self.locations[category].append(location)
        
        # Connect to the road network
        self.road_network.connect_location_to_nearest_road(location)
        
        print(f"City grew! Added new {loc_type}: {name}")
        return location
