"""
Location module for AI City Simulator.
Represents different locations in the city.
"""
from datetime import datetime, time


class Location:
    """Represents a location in the city."""
    
    def __init__(self, name, location_type, category, x, y, capacity=10):
        """
        Initialize a location.
        
        Args:
            name (str): Name of the location
            location_type (str): Type of location (e.g., House, Restaurant)
            category (str): Category of location (e.g., residential, commercial)
            x (float): X coordinate on the city map
            y (float): Y coordinate on the city map
            capacity (int): Maximum number of agents that can be at this location
        """
        self.name = name
        self.location_type = location_type
        self.category = category
        self.x = x
        self.y = y
        self.capacity = capacity
        
        # Current agents at this location
        self.agents = []
        
        # Opening and closing hours (24-hour format)
        self.opening_hours = self._get_default_hours()
        
        # Properties specific to this location
        self.properties = {}
        
        # Initialize location-specific properties
        self._initialize_properties()
    
    def _get_default_hours(self):
        """Get default opening hours based on location type."""
        # Default is closed
        hours = {
            'monday': (None, None),
            'tuesday': (None, None),
            'wednesday': (None, None),
            'thursday': (None, None),
            'friday': (None, None),
            'saturday': (None, None),
            'sunday': (None, None),
        }
        
        # Set hours based on location type
        if self.location_type in ['Grocery Store', 'Shopping Mall']:
            # 8 AM to 10 PM
            for day in hours:
                hours[day] = (time(8, 0), time(22, 0))
        
        elif self.location_type in ['Restaurant', 'Coffee Shop']:
            # 7 AM to 11 PM
            for day in hours:
                hours[day] = (time(7, 0), time(23, 0))
        
        elif self.location_type == 'Bar':
            # 4 PM to 2 AM
            for day in hours:
                hours[day] = (time(16, 0), time(2, 0))
        
        elif self.location_type in ['Elementary School', 'High School']:
            # 8 AM to 3 PM, weekdays only
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                hours[day] = (time(8, 0), time(15, 0))
        
        elif self.location_type == 'College':
            # 8 AM to 10 PM, weekdays only
            for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                hours[day] = (time(8, 0), time(22, 0))
        
        elif self.location_type == 'Gym':
            # 6 AM to 11 PM
            for day in hours:
                hours[day] = (time(6, 0), time(23, 0))
        
        elif self.location_type in ['Police Station', 'Hospital', 'Fire Station']:
            # 24/7
            for day in hours:
                hours[day] = (time(0, 0), time(23, 59))
        
        elif self.location_type in ['House', 'Apartment', 'Condo', 'Senior Living']:
            # Homes are always "open"
            for day in hours:
                hours[day] = (time(0, 0), time(23, 59))
        
        return hours
    
    def _initialize_properties(self):
        """Initialize properties specific to this location type."""
        if self.location_type in ['Restaurant', 'Coffee Shop', 'Bar']:
            self.properties['price_level'] = random.randint(1, 5)  # 1 = cheap, 5 = expensive
            self.properties['quality'] = random.randint(1, 5)      # 1 = poor, 5 = excellent
            self.properties['cuisine'] = random.choice(['American', 'Italian', 'Mexican', 'Chinese', 'Indian', 'Japanese'])
        
        elif self.location_type in ['Grocery Store', 'Shopping Mall']:
            self.properties['price_level'] = random.randint(1, 5)
            self.properties['size'] = random.choice(['Small', 'Medium', 'Large'])
        
        elif self.location_type in ['Elementary School', 'High School', 'College']:
            self.properties['quality'] = random.randint(1, 5)
            self.properties['size'] = random.choice(['Small', 'Medium', 'Large'])
        
        elif self.location_type == 'Gym':
            self.properties['price_level'] = random.randint(1, 5)
            self.properties['equipment_quality'] = random.randint(1, 5)
        
        elif self.location_type in ['House', 'Apartment', 'Condo']:
            self.properties['price_level'] = random.randint(1, 5)
            self.properties['size'] = random.choice(['Small', 'Medium', 'Large'])
            self.properties['quality'] = random.randint(1, 5)
    
    def is_open(self, current_time):
        """
        Check if the location is open at the given time.
        
        Args:
            current_time (datetime): Current time to check
            
        Returns:
            bool: True if the location is open, False otherwise
        """
        # Get day of week
        day = current_time.strftime('%A').lower()
        
        # Get opening hours for this day
        open_time, close_time = self.opening_hours.get(day, (None, None))
        
        # If no hours set, location is closed
        if open_time is None or close_time is None:
            return False
        
        # Get current time as time object
        current_time_obj = current_time.time()
        
        # Handle special case for places that close after midnight
        if close_time < open_time:
            return current_time_obj >= open_time or current_time_obj <= close_time
        else:
            return open_time <= current_time_obj <= close_time
    
    def add_agent(self, agent):
        """
        Add an agent to this location.
        
        Args:
            agent: Agent to add
            
        Returns:
            bool: True if agent was added, False if location is at capacity
        """
        if len(self.agents) >= self.capacity:
            return False
        
        self.agents.append(agent)
        return True
    
    def remove_agent(self, agent):
        """
        Remove an agent from this location.
        
        Args:
            agent: Agent to remove
            
        Returns:
            bool: True if agent was removed, False if agent was not at this location
        """
        if agent in self.agents:
            self.agents.remove(agent)
            return True
        return False
    
    def get_agent_count(self):
        """Get the number of agents currently at this location."""
        return len(self.agents)
    
    def is_full(self):
        """Check if the location is at capacity."""
        return len(self.agents) >= self.capacity
    
    def update(self, current_time):
        """
        Update the location state based on the current time.
        
        Args:
            current_time (datetime): Current simulation time
        """
        # For now, we don't need to do anything here
        pass
    
    def __str__(self):
        """String representation of the location."""
        return f"{self.name} ({self.location_type})"


# Import at the end to avoid circular imports
import random
