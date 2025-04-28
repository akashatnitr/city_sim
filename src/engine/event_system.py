"""
Event system module for AI City Simulator.
Manages special events and occurrences in the city.
"""
import random


class EventSystem:
    """Manages special events in the city."""
    
    def __init__(self, simulation, config):
        """
        Initialize the event system.
        
        Args:
            simulation: The simulation instance
            config (dict): Configuration dictionary for events
        """
        self.simulation = simulation
        self.config = config
        self.enable_events = config.get('enable_events', True)
        self.event_probability = config.get('event_probability', 0.001)
        
        # Event types
        self.event_types = {
            'festival': {
                'duration': 1000,
                'impact_radius': 200,
                'description': 'A city festival with music, food, and entertainment.'
            },
            'parade': {
                'duration': 500,
                'impact_radius': 150,
                'description': 'A parade moving through the streets.'
            },
            'protest': {
                'duration': 800,
                'impact_radius': 100,
                'description': 'A group of citizens protesting.'
            },
            'construction': {
                'duration': 2000,
                'impact_radius': 50,
                'description': 'Road construction causing delays.'
            },
            'fire': {
                'duration': 300,
                'impact_radius': 100,
                'description': 'A building fire requiring emergency response.'
            },
            'power_outage': {
                'duration': 1000,
                'impact_radius': 300,
                'description': 'A power outage affecting part of the city.'
            },
            'sports_game': {
                'duration': 500,
                'impact_radius': 200,
                'description': 'A sports game drawing a large crowd.'
            },
            'concert': {
                'duration': 400,
                'impact_radius': 150,
                'description': 'A concert drawing a large crowd.'
            },
        }
        
        # Active events
        self.active_events = []
        
        # Event statistics
        self.stats = {
            'total_events': 0,
            'events_by_type': {event_type: 0 for event_type in self.event_types},
        }
    
    def update(self):
        """Update the event system."""
        if not self.enable_events:
            return
        
        # Update active events
        self._update_active_events()
        
        # Generate new events
        self._generate_events()
    
    def _update_active_events(self):
        """Update active events."""
        # Remove expired events
        self.active_events = [event for event in self.active_events if not event['expired']]
        
        # Update each active event
        for event in self.active_events:
            # Increment duration
            event['elapsed'] += 1
            
            # Check if event has expired
            if event['elapsed'] >= event['duration']:
                event['expired'] = True
                print(f"Event ended: {event['type']} at {event['location'].name}")
    
    def _generate_events(self):
        """Generate new events."""
        # Check if an event occurs
        if random.random() < self.event_probability * self.simulation.speed:
            self._create_event()
    
    def _create_event(self):
        """Create a new event."""
        # Choose an event type
        event_type = random.choice(list(self.event_types.keys()))
        event_info = self.event_types[event_type]
        
        # Choose a location for the event
        location = self._choose_event_location(event_type)
        
        # Create the event
        event = {
            'type': event_type,
            'location': location,
            'x': location.x,
            'y': location.y,
            'duration': event_info['duration'],
            'elapsed': 0,
            'impact_radius': event_info['impact_radius'],
            'description': event_info['description'],
            'expired': False,
        }
        
        # Add to active events
        self.active_events.append(event)
        
        # Update statistics
        self.stats['total_events'] += 1
        self.stats['events_by_type'][event_type] += 1
        
        print(f"Event started: {event_type} at {location.name}")
    
    def _choose_event_location(self, event_type):
        """
        Choose a location for an event based on the event type.
        
        Args:
            event_type (str): Type of event
            
        Returns:
            Location: The chosen location
        """
        city = self.simulation.city
        
        if event_type == 'festival' or event_type == 'concert':
            # Festivals and concerts happen in parks or stadiums
            locations = city.get_locations_by_type('Park') + city.get_locations_by_type('Sports Stadium')
            
        elif event_type == 'parade':
            # Parades happen on main streets (use commercial areas as proxy)
            locations = city.get_locations_by_category('commercial')
            
        elif event_type == 'protest':
            # Protests happen at government buildings or parks
            locations = city.get_locations_by_type('City Hall') + city.get_locations_by_type('Park')
            
        elif event_type == 'construction':
            # Construction can happen anywhere
            locations = city.get_all_locations()
            
        elif event_type == 'fire':
            # Fires happen in buildings
            locations = city.get_locations_by_category('residential') + city.get_locations_by_category('commercial')
            
        elif event_type == 'power_outage':
            # Power outages affect residential areas
            locations = city.get_locations_by_category('residential')
            
        elif event_type == 'sports_game':
            # Sports games happen at stadiums
            locations = city.get_locations_by_type('Sports Stadium')
            
        else:
            # Default to any location
            locations = city.get_all_locations()
        
        if not locations:
            # Fallback to any location
            locations = city.get_all_locations()
        
        # Choose a random location
        return random.choice(locations)
    
    def get_events_in_area(self, x, y, radius):
        """
        Get all events in a circular area.
        
        Args:
            x (float): X coordinate of the center
            y (float): Y coordinate of the center
            radius (float): Radius of the area
            
        Returns:
            list: List of events within the area
        """
        return [event for event in self.active_events 
                if ((event['x'] - x) ** 2 + (event['y'] - y) ** 2) ** 0.5 <= radius]
    
    def get_active_events(self):
        """
        Get all active events.
        
        Returns:
            list: List of active events
        """
        return self.active_events
