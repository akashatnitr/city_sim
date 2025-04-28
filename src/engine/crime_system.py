"""
Crime system module for AI City Simulator.
Manages criminal activities and law enforcement.
"""
import random
import math


class CrimeSystem:
    """Manages criminal activities and law enforcement."""
    
    def __init__(self, simulation, config):
        """
        Initialize the crime system.
        
        Args:
            simulation: The simulation instance
            config (dict): Configuration dictionary for crime
        """
        self.simulation = simulation
        self.config = config
        self.enable_crime = config.get('enable_crime', True)
        self.base_crime_rate = config.get('crime_rate', 0.01)
        
        # Crime types and their severity (0-1)
        self.crime_types = {
            'theft': 0.3,
            'vandalism': 0.2,
            'assault': 0.7,
            'robbery': 0.6,
            'burglary': 0.5,
        }
        
        # Active crimes
        self.active_crimes = []
        
        # Crime statistics
        self.stats = {
            'total_crimes': 0,
            'crimes_by_type': {crime_type: 0 for crime_type in self.crime_types},
            'solved_crimes': 0,
            'arrests': 0,
        }
        
        # Crime hotspots
        self.hotspots = []
    
    def update(self):
        """Update the crime system."""
        if not self.enable_crime:
            return
        
        # Update active crimes
        self._update_active_crimes()
        
        # Generate new crimes
        self._generate_crimes()
        
        # Update hotspots
        self._update_hotspots()
    
    def _update_active_crimes(self):
        """Update active crimes."""
        # Remove expired crimes
        self.active_crimes = [crime for crime in self.active_crimes if not crime['expired']]
        
        # Update each active crime
        for crime in self.active_crimes:
            # Increment duration
            crime['duration'] += 1
            
            # Check if crime has expired
            if crime['duration'] >= crime['max_duration']:
                crime['expired'] = True
                continue
            
            # Check if police are nearby
            police_nearby = self._check_police_nearby(crime['x'], crime['y'])
            
            if police_nearby:
                # Police have a chance to solve the crime
                if random.random() < 0.2:
                    crime['expired'] = True
                    crime['solved'] = True
                    self.stats['solved_crimes'] += 1
                    
                    # Check if criminal is caught
                    if random.random() < 0.5:
                        self.stats['arrests'] += 1
                        
                        # If the criminal is an agent, update their stats
                        if crime['criminal'] is not None:
                            crime['criminal'].stats['crimes_committed'] += 1
    
    def _generate_crimes(self):
        """Generate new crimes."""
        # Get the current crime rate
        crime_rate = self._calculate_crime_rate()
        
        # Check if a crime occurs
        if random.random() < crime_rate:
            self._create_crime()
    
    def _calculate_crime_rate(self):
        """
        Calculate the current crime rate based on various factors.
        
        Returns:
            float: Current crime rate
        """
        # Base crime rate
        crime_rate = self.base_crime_rate
        
        # Adjust for time of day
        day_phase = self.simulation.get_day_phase()
        if day_phase == 'night':
            crime_rate *= 2.0  # More crime at night
        elif day_phase == 'morning':
            crime_rate *= 0.5  # Less crime in the morning
        
        # Adjust for weather
        weather_effect = self.simulation.weather_system.get_weather_effect('crime_modifier')
        crime_rate *= weather_effect
        
        # Adjust for police presence
        police_count = len(self.simulation.agent_manager.get_agents_by_type('police'))
        criminal_count = len(self.simulation.agent_manager.get_agents_by_type('criminal'))
        
        if police_count > 0:
            police_factor = 1.0 - 0.1 * min(10, police_count)  # More police = less crime
            crime_rate *= max(0.1, police_factor)
        
        if criminal_count > 0:
            criminal_factor = 1.0 + 0.1 * min(10, criminal_count)  # More criminals = more crime
            crime_rate *= criminal_factor
        
        return crime_rate * self.simulation.speed
    
    def _create_crime(self):
        """Create a new crime incident."""
        # Choose a crime type
        crime_type = random.choice(list(self.crime_types.keys()))
        severity = self.crime_types[crime_type]
        
        # Choose a location for the crime
        location = self._choose_crime_location()
        
        # Choose a criminal (if available)
        criminal = self._choose_criminal()
        
        # Create the crime
        crime = {
            'type': crime_type,
            'severity': severity,
            'x': location.x,
            'y': location.y,
            'location': location,
            'criminal': criminal,
            'duration': 0,
            'max_duration': int(100 * severity),  # More severe crimes last longer
            'expired': False,
            'solved': False,
        }
        
        # Add to active crimes
        self.active_crimes.append(crime)
        
        # Update statistics
        self.stats['total_crimes'] += 1
        self.stats['crimes_by_type'][crime_type] += 1
        
        # Add a hotspot
        self._add_hotspot(location.x, location.y, severity)
        
        # If there's a criminal agent, update their stats
        if criminal is not None:
            criminal.stats['crimes_committed'] += 1
        
        print(f"Crime occurred: {crime_type} at {location.name}")
    
    def _choose_crime_location(self):
        """
        Choose a location for a crime to occur.
        
        Returns:
            Location: The chosen location
        """
        # Different location types have different crime probabilities
        location_weights = {
            'residential': 0.3,
            'commercial': 0.4,
            'educational': 0.1,
            'transportation': 0.1,
            'recreation': 0.05,
            'service': 0.05,
        }
        
        # Choose a category based on weights
        category = random.choices(list(location_weights.keys()), 
                                 weights=list(location_weights.values()))[0]
        
        # Get locations in that category
        locations = self.simulation.city.get_locations_by_category(category)
        
        if not locations:
            # Fallback to any location
            locations = self.simulation.city.get_all_locations()
        
        # Choose a random location
        return random.choice(locations)
    
    def _choose_criminal(self):
        """
        Choose a criminal agent to commit the crime.
        
        Returns:
            Agent or None: The chosen criminal agent, or None if no criminals available
        """
        # Get all criminal agents
        criminals = self.simulation.agent_manager.get_agents_by_type('criminal')
        
        if not criminals:
            return None
        
        # Filter to only include criminals who are not currently in jail
        active_criminals = [c for c in criminals if c.state != 'jail']
        
        if not active_criminals:
            return None
        
        # Choose a random criminal
        return random.choice(active_criminals)
    
    def _check_police_nearby(self, x, y, radius=100):
        """
        Check if there are police officers near a location.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            radius (float): Radius to check
            
        Returns:
            bool: True if police are nearby, False otherwise
        """
        # Get all police agents
        police = self.simulation.agent_manager.get_agents_by_type('police')
        
        # Check if any are within the radius
        for officer in police:
            dx = officer.x - x
            dy = officer.y - y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= radius:
                return True
        
        return False
    
    def _add_hotspot(self, x, y, intensity):
        """
        Add a crime hotspot.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            intensity (float): Intensity of the hotspot
        """
        # Create a new hotspot
        hotspot = {
            'x': x,
            'y': y,
            'intensity': intensity,
            'age': 0,
            'max_age': 1000,  # Hotspots last for a while
        }
        
        # Add to hotspots
        self.hotspots.append(hotspot)
    
    def _update_hotspots(self):
        """Update crime hotspots."""
        # Increment age and remove expired hotspots
        for hotspot in self.hotspots:
            hotspot['age'] += 1
            hotspot['intensity'] *= 0.999  # Gradually decrease intensity
        
        # Remove expired hotspots
        self.hotspots = [h for h in self.hotspots 
                        if h['age'] < h['max_age'] and h['intensity'] > 0.1]
    
    def get_crimes_in_area(self, x, y, radius):
        """
        Get all crimes in a circular area.
        
        Args:
            x (float): X coordinate of the center
            y (float): Y coordinate of the center
            radius (float): Radius of the area
            
        Returns:
            list: List of crimes within the area
        """
        return [crime for crime in self.active_crimes 
                if ((crime['x'] - x) ** 2 + (crime['y'] - y) ** 2) ** 0.5 <= radius]
    
    def get_hotspots(self):
        """
        Get all crime hotspots.
        
        Returns:
            list: List of crime hotspots
        """
        return self.hotspots
    
    def get_crime_heatmap(self):
        """
        Get a crime heatmap.
        
        Returns:
            list: List of (x, y, intensity) tuples for the heatmap
        """
        return [(h['x'], h['y'], h['intensity']) for h in self.hotspots]
