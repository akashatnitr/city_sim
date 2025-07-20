import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class EventManager:
    """Manages dynamic events in the city simulation"""
    
    def __init__(self, simulation_engine):
        self.simulation_engine = simulation_engine
        self.active_events = {}  # event_id -> event data
        self.event_queue = []  # Scheduled events
        self.event_templates = self._initialize_event_templates()
        self.last_random_event = datetime.utcnow()
        self.random_event_interval = timedelta(hours=6)  # Random event every 6 hours on average
    
    def _initialize_event_templates(self) -> Dict[str, Dict]:
        """Initialize templates for different types of events"""
        return {
            'traffic_accident': {
                'name': 'Traffic Accident',
                'type': 'emergency',
                'severity': 'medium',
                'duration_range': (30, 120),  # minutes
                'effects': {
                    'road_blocks': True,
                    'traffic_increase': 2.0,
                    'emergency_services': True
                },
                'probability': 0.1
            },
            'fire_emergency': {
                'name': 'Building Fire',
                'type': 'emergency',
                'severity': 'high',
                'duration_range': (60, 240),
                'effects': {
                    'location_evacuation': True,
                    'emergency_services': True,
                    'traffic_increase': 1.5
                },
                'probability': 0.05
            },
            'power_outage': {
                'name': 'Power Outage',
                'type': 'infrastructure',
                'severity': 'medium',
                'duration_range': (120, 480),
                'effects': {
                    'location_closure': True,
                    'reduced_services': True
                },
                'probability': 0.08
            },
            'public_holiday': {
                'name': 'Public Holiday',
                'type': 'holiday',
                'severity': 'low',
                'duration_range': (480, 1440),  # 8-24 hours
                'effects': {
                    'reduced_work': True,
                    'increased_leisure': True,
                    'location_closures': ['office', 'school']
                },
                'probability': 0.02
            },
            'festival': {
                'name': 'City Festival',
                'type': 'social',
                'severity': 'low',
                'duration_range': (240, 720),  # 4-12 hours
                'effects': {
                    'increased_foot_traffic': True,
                    'location_crowding': True,
                    'traffic_increase': 1.3
                },
                'probability': 0.03
            },
            'weather_warning': {
                'name': 'Severe Weather Warning',
                'type': 'weather',
                'severity': 'high',
                'duration_range': (60, 360),
                'effects': {
                    'movement_restriction': True,
                    'location_closures': ['outdoor'],
                    'increased_energy_consumption': True
                },
                'probability': 0.06
            },
            'construction': {
                'name': 'Road Construction',
                'type': 'infrastructure',
                'severity': 'low',
                'duration_range': (1440, 10080),  # 1-7 days
                'effects': {
                    'road_blocks': True,
                    'traffic_increase': 1.4,
                    'noise_pollution': True
                },
                'probability': 0.04
            },
            'epidemic_outbreak': {
                'name': 'Disease Outbreak',
                'type': 'health',
                'severity': 'critical',
                'duration_range': (2880, 20160),  # 2-14 days
                'effects': {
                    'movement_restriction': True,
                    'location_closures': ['entertainment', 'restaurant'],
                    'health_impact': True,
                    'reduced_capacity': 0.5
                },
                'probability': 0.01
            },
            'sports_event': {
                'name': 'Major Sports Event',
                'type': 'social',
                'severity': 'medium',
                'duration_range': (180, 360),
                'effects': {
                    'traffic_increase': 2.0,
                    'location_crowding': True,
                    'increased_foot_traffic': True
                },
                'probability': 0.02
            },
            'protest': {
                'name': 'Public Protest',
                'type': 'social',
                'severity': 'medium',
                'duration_range': (120, 480),
                'effects': {
                    'road_blocks': True,
                    'traffic_increase': 1.8,
                    'police_presence': True
                },
                'probability': 0.03
            }
        }
    
    def process_events(self, current_time: datetime):
        """Process all active events and check for new ones"""
        # Update active events
        self._update_active_events(current_time)
        
        # Process scheduled events
        self._process_scheduled_events(current_time)
        
        # Generate random events
        self._generate_random_events(current_time)
    
    def _update_active_events(self, current_time: datetime):
        """Update and expire active events"""
        expired_events = []
        
        for event_id, event_data in self.active_events.items():
            end_time = datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00'))
            
            if current_time >= end_time:
                # Event has expired
                expired_events.append(event_id)
                self._end_event(event_id, event_data)
            else:
                # Update event effects
                self._apply_event_effects(event_data, current_time)
        
        # Remove expired events
        for event_id in expired_events:
            del self.active_events[event_id]
    
    def _process_scheduled_events(self, current_time: datetime):
        """Process events in the event queue"""
        triggered_events = []
        
        for i, event_data in enumerate(self.event_queue):
            start_time = datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00'))
            
            if current_time >= start_time:
                # Trigger the event
                self._start_event(event_data)
                triggered_events.append(i)
        
        # Remove triggered events from queue
        for i in reversed(triggered_events):
            del self.event_queue[i]
    
    def _generate_random_events(self, current_time: datetime):
        """Generate random events based on probability"""
        if current_time - self.last_random_event < self.random_event_interval:
            return
        
        # Check if we should generate a random event
        if random.random() < 0.3:  # 30% chance per interval
            event_type = self._select_random_event_type()
            if event_type:
                self._create_random_event(event_type, current_time)
        
        self.last_random_event = current_time
    
    def _select_random_event_type(self) -> Optional[str]:
        """Select a random event type based on probabilities"""
        total_probability = sum(template['probability'] for template in self.event_templates.values())
        r = random.uniform(0, total_probability)
        
        cumulative = 0
        for event_type, template in self.event_templates.items():
            cumulative += template['probability']
            if r <= cumulative:
                return event_type
        
        return None
    
    def _create_random_event(self, event_type: str, current_time: datetime):
        """Create a random event of the specified type"""
        template = self.event_templates[event_type]
        
        # Generate random duration
        min_duration, max_duration = template['duration_range']
        duration = random.randint(min_duration, max_duration)
        
        # Select random location if needed
        location_id = self._select_event_location(event_type)
        
        event_data = {
            'name': template['name'],
            'type': template['type'],
            'severity': template['severity'],
            'start_time': current_time.isoformat(),
            'end_time': (current_time + timedelta(minutes=duration)).isoformat(),
            'location_id': location_id,
            'effects': template['effects'].copy(),
            'description': f"Random {template['name'].lower()} event",
            'is_active': True
        }
        
        self._start_event(event_data)
    
    def _select_event_location(self, event_type: str) -> Optional[int]:
        """Select appropriate location for an event"""
        locations = self.simulation_engine.locations
        
        if not locations:
            return None
        
        # Filter locations based on event type
        suitable_locations = []
        
        if event_type in ['fire_emergency', 'power_outage']:
            # Any building
            suitable_locations = [
                loc_id for loc_id, loc_data in locations.items()
                if loc_data['type'] in ['office', 'home', 'restaurant', 'shop']
            ]
        elif event_type in ['traffic_accident', 'construction']:
            # Near roads - select random location
            suitable_locations = list(locations.keys())
        elif event_type in ['festival', 'sports_event', 'protest']:
            # Public spaces
            suitable_locations = [
                loc_id for loc_id, loc_data in locations.items()
                if loc_data['type'] in ['park', 'square', 'stadium', 'plaza']
            ]
        else:
            # Any location
            suitable_locations = list(locations.keys())
        
        return random.choice(suitable_locations) if suitable_locations else None
    
    def _start_event(self, event_data: Dict):
        """Start a new event"""
        # Generate unique event ID
        event_id = len(self.active_events) + 1
        event_data['id'] = event_id
        
        # Add to active events
        self.active_events[event_id] = event_data
        
        # Apply initial effects
        self._apply_event_effects(event_data, datetime.utcnow())
        
        # Log event start
        self.simulation_engine.log_event('event', 'started', event_data)
        
        # Emit event notification
        self.simulation_engine.emit_update('event_started', event_data)
        
        print(f"Event started: {event_data['name']} at location {event_data.get('location_id', 'city-wide')}")
    
    def _end_event(self, event_id: int, event_data: Dict):
        """End an active event"""
        # Remove event effects
        self._remove_event_effects(event_data)
        
        # Log event end
        self.simulation_engine.log_event('event', 'ended', event_data)
        
        # Emit event notification
        self.simulation_engine.emit_update('event_ended', event_data)
        
        print(f"Event ended: {event_data['name']}")
    
    def _apply_event_effects(self, event_data: Dict, current_time: datetime):
        """Apply effects of an event to the simulation"""
        effects = event_data.get('effects', {})
        location_id = event_data.get('location_id')
        
        # Apply road blocks
        if effects.get('road_blocks'):
            self._apply_road_blocks(location_id)
        
        # Apply traffic increases
        if 'traffic_increase' in effects:
            self._apply_traffic_increase(effects['traffic_increase'], location_id)
        
        # Apply location closures
        if effects.get('location_closure') or effects.get('location_closures'):
            self._apply_location_closures(effects, location_id)
        
        # Apply capacity reductions
        if 'reduced_capacity' in effects:
            self._apply_capacity_reduction(effects['reduced_capacity'], location_id)
        
        # Apply agent behavior modifications
        self._apply_agent_effects(effects, event_data)
    
    def _remove_event_effects(self, event_data: Dict):
        """Remove effects of an event from the simulation"""
        effects = event_data.get('effects', {})
        location_id = event_data.get('location_id')
        
        # Remove road blocks
        if effects.get('road_blocks'):
            self._remove_road_blocks(location_id)
        
        # Reset traffic
        if 'traffic_increase' in effects:
            self._reset_traffic(location_id)
        
        # Reopen locations
        if effects.get('location_closure') or effects.get('location_closures'):
            self._reopen_locations(location_id)
        
        # Reset capacity
        if 'reduced_capacity' in effects:
            self._reset_capacity(location_id)
    
    def _apply_road_blocks(self, location_id: Optional[int]):
        """Apply road blocks around a location"""
        if not location_id or location_id not in self.simulation_engine.locations:
            return
        
        # Find roads connected to the location
        roads = self.simulation_engine.roads
        for road_id, road_data in roads.items():
            if (road_data['from_location_id'] == location_id or 
                road_data['to_location_id'] == location_id):
                road_data['current_traffic'] = max(road_data.get('current_traffic', 1.0), 3.0)
    
    def _apply_traffic_increase(self, multiplier: float, location_id: Optional[int]):
        """Apply traffic increase"""
        roads = self.simulation_engine.roads
        
        if location_id:
            # Apply to roads near the location
            for road_id, road_data in roads.items():
                if (road_data['from_location_id'] == location_id or 
                    road_data['to_location_id'] == location_id):
                    road_data['current_traffic'] *= multiplier
        else:
            # Apply city-wide
            for road_data in roads.values():
                road_data['current_traffic'] *= multiplier
    
    def _apply_location_closures(self, effects: Dict, location_id: Optional[int]):
        """Apply location closures"""
        locations = self.simulation_engine.locations
        
        if location_id and location_id in locations:
            # Close specific location
            locations[location_id]['is_open'] = False
        
        # Close locations by type
        closure_types = effects.get('location_closures', [])
        for loc_data in locations.values():
            if loc_data['type'] in closure_types:
                loc_data['is_open'] = False
    
    def _apply_capacity_reduction(self, reduction_factor: float, location_id: Optional[int]):
        """Apply capacity reduction to locations"""
        locations = self.simulation_engine.locations
        
        if location_id and location_id in locations:
            location = locations[location_id]
            location['capacity'] = int(location['capacity'] * reduction_factor)
        else:
            # Apply to all locations
            for location in locations.values():
                location['capacity'] = int(location['capacity'] * reduction_factor)
    
    def _apply_agent_effects(self, effects: Dict, event_data: Dict):
        """Apply effects to agents"""
        # This would modify agent behaviors based on the event
        # For now, just log the effect
        if effects.get('movement_restriction'):
            print(f"Movement restrictions applied due to {event_data['name']}")
        
        if effects.get('health_impact'):
            print(f"Health impacts applied due to {event_data['name']}")
    
    def _remove_road_blocks(self, location_id: Optional[int]):
        """Remove road blocks"""
        if not location_id:
            return
        
        roads = self.simulation_engine.roads
        for road_id, road_data in roads.items():
            if (road_data['from_location_id'] == location_id or 
                road_data['to_location_id'] == location_id):
                road_data['current_traffic'] = 1.0  # Reset to normal
    
    def _reset_traffic(self, location_id: Optional[int]):
        """Reset traffic to normal levels"""
        roads = self.simulation_engine.roads
        
        if location_id:
            for road_id, road_data in roads.items():
                if (road_data['from_location_id'] == location_id or 
                    road_data['to_location_id'] == location_id):
                    road_data['current_traffic'] = 1.0
        else:
            for road_data in roads.values():
                road_data['current_traffic'] = 1.0
    
    def _reopen_locations(self, location_id: Optional[int]):
        """Reopen closed locations"""
        locations = self.simulation_engine.locations
        
        if location_id and location_id in locations:
            locations[location_id]['is_open'] = True
        else:
            # Reopen all locations
            for location in locations.values():
                location['is_open'] = True
    
    def _reset_capacity(self, location_id: Optional[int]):
        """Reset location capacity to original values"""
        # This would require storing original capacity values
        # For now, just set to a reasonable default
        locations = self.simulation_engine.locations
        
        if location_id and location_id in locations:
            locations[location_id]['capacity'] = 100  # Default capacity
        else:
            for location in locations.values():
                location['capacity'] = 100
    
    def add_event(self, event_data: Dict):
        """Add a new event to the simulation"""
        if 'start_time' in event_data:
            # Scheduled event
            self.event_queue.append(event_data)
        else:
            # Immediate event
            event_data['start_time'] = datetime.utcnow().isoformat()
            self._start_event(event_data)
    
    def get_active_events(self) -> List[Dict]:
        """Get all currently active events"""
        return list(self.active_events.values())
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict]:
        """Get event by ID"""
        return self.active_events.get(event_id)
    
    def cancel_event(self, event_id: int) -> bool:
        """Cancel an active event"""
        if event_id in self.active_events:
            event_data = self.active_events[event_id]
            self._end_event(event_id, event_data)
            del self.active_events[event_id]
            return True
        return False

