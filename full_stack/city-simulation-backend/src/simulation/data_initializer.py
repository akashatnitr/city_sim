import random
import json
from datetime import datetime, timedelta
from src.models.user import db
from src.models.agent import Agent
from src.models.location import Location, Road, TransitStop
from src.models.event import SimulationState, Event, WeatherCondition

class DataInitializer:
    """Initialize simulation with sample data"""
    
    def __init__(self):
        self.locations_data = []
        self.roads_data = []
        self.agents_data = []
        self.events_data = []
    
    def initialize_city(self, city_size='medium'):
        """Initialize a complete city with locations, roads, and agents"""
        print("Initializing city simulation data...")
        
        # Clear existing data
        self._clear_existing_data()
        
        # Create locations
        self._create_locations(city_size)
        
        # Create roads connecting locations
        self._create_roads()
        
        # Create transit stops
        self._create_transit_stops()
        
        # Create sample agents
        self._create_sample_agents()
        
        # Create initial events
        self._create_initial_events()
        
        # Initialize simulation state
        self._initialize_simulation_state()
        
        print(f"City initialized with {len(self.locations_data)} locations, "
              f"{len(self.roads_data)} roads, and {len(self.agents_data)} agents")
    
    def _clear_existing_data(self):
        """Clear existing simulation data"""
        try:
            Agent.query.delete()
            Location.query.delete()
            Road.query.delete()
            TransitStop.query.delete()
            Event.query.delete()
            WeatherCondition.query.delete()
            db.session.commit()
        except Exception as e:
            print(f"Error clearing data: {e}")
            db.session.rollback()
    
    def _create_locations(self, city_size):
        """Create city locations"""
        location_configs = {
            'small': {
                'residential': 20,
                'office': 8,
                'school': 3,
                'restaurant': 10,
                'shop': 12,
                'hospital': 2,
                'park': 5,
                'transit': 4
            },
            'medium': {
                'residential': 40,
                'office': 15,
                'school': 6,
                'restaurant': 20,
                'shop': 25,
                'hospital': 4,
                'park': 10,
                'transit': 8
            },
            'large': {
                'residential': 80,
                'office': 30,
                'school': 12,
                'restaurant': 40,
                'shop': 50,
                'hospital': 8,
                'park': 20,
                'transit': 15
            }
        }
        
        config = location_configs.get(city_size, location_configs['medium'])
        
        # City grid parameters
        grid_size = 20  # 20x20 km city
        
        location_id = 1
        
        for location_type, count in config.items():
            for i in range(count):
                # Generate random position within city grid
                x = random.uniform(-grid_size/2, grid_size/2)
                y = random.uniform(-grid_size/2, grid_size/2)
                
                location_data = self._generate_location_data(location_type, location_id, x, y)
                
                location = Location(
                    name=location_data['name'],
                    type=location_data['type'],
                    x=x,
                    y=y,
                    capacity=location_data['capacity'],
                    is_open=location_data['is_open']
                )
                
                if location_data.get('opening_hours'):
                    location.set_opening_hours(location_data['opening_hours'])
                if location_data.get('services'):
                    location.set_services(location_data['services'])
                if location_data.get('properties'):
                    location.set_properties(location_data['properties'])
                
                db.session.add(location)
                self.locations_data.append(location_data)
                location_id += 1
        
        db.session.commit()
    
    def _generate_location_data(self, location_type, location_id, x, y):
        """Generate location data based on type"""
        location_templates = {
            'residential': {
                'names': ['Sunset Apartments', 'Oak Street Homes', 'Riverside Complex', 'Downtown Lofts'],
                'capacity': (50, 200),
                'opening_hours': None,
                'services': ['parking', 'security'],
                'properties': {'residential_units': random.randint(20, 100)}
            },
            'office': {
                'names': ['Tech Tower', 'Business Center', 'Corporate Plaza', 'Innovation Hub'],
                'capacity': (100, 500),
                'opening_hours': {'monday-friday': '08:00-18:00'},
                'services': ['parking', 'cafeteria', 'meeting_rooms'],
                'properties': {'floors': random.randint(5, 20)}
            },
            'school': {
                'names': ['Central Elementary', 'Riverside High School', 'City University', 'Community College'],
                'capacity': (200, 2000),
                'opening_hours': {'monday-friday': '07:00-17:00'},
                'services': ['library', 'cafeteria', 'sports_facilities'],
                'properties': {'students': random.randint(500, 3000)}
            },
            'restaurant': {
                'names': ['Bella Vista', 'The Corner Cafe', 'Dragon Palace', 'Burger Junction'],
                'capacity': (30, 150),
                'opening_hours': {'daily': '11:00-22:00'},
                'services': ['takeout', 'delivery', 'parking'],
                'properties': {'cuisine': random.choice(['italian', 'american', 'chinese', 'mexican'])}
            },
            'shop': {
                'names': ['SuperMart', 'Fashion Boutique', 'Electronics Store', 'Book Corner'],
                'capacity': (50, 300),
                'opening_hours': {'daily': '09:00-21:00'},
                'services': ['parking', 'customer_service'],
                'properties': {'category': random.choice(['grocery', 'clothing', 'electronics', 'books'])}
            },
            'hospital': {
                'names': ['City General Hospital', 'St. Mary Medical Center', 'Emergency Clinic'],
                'capacity': (100, 500),
                'opening_hours': {'daily': '24/7'},
                'services': ['emergency', 'parking', 'pharmacy'],
                'properties': {'beds': random.randint(50, 300)}
            },
            'park': {
                'names': ['Central Park', 'Riverside Gardens', 'Oak Grove Park', 'Memorial Square'],
                'capacity': (200, 1000),
                'opening_hours': {'daily': '06:00-22:00'},
                'services': ['playground', 'walking_trails', 'parking'],
                'properties': {'area_hectares': random.randint(5, 50)}
            },
            'transit': {
                'names': ['Central Station', 'Metro Hub', 'Bus Terminal', 'Transit Center'],
                'capacity': (500, 2000),
                'opening_hours': {'daily': '05:00-24:00'},
                'services': ['ticketing', 'waiting_area', 'parking'],
                'properties': {'platforms': random.randint(4, 12)}
            }
        }
        
        template = location_templates.get(location_type, location_templates['shop'])
        
        name = f"{random.choice(template['names'])} #{location_id}"
        capacity = random.randint(*template['capacity'])
        
        return {
            'id': location_id,
            'name': name,
            'type': location_type,
            'x': x,
            'y': y,
            'capacity': capacity,
            'is_open': True,
            'opening_hours': template.get('opening_hours'),
            'services': template.get('services', []),
            'properties': template.get('properties', {})
        }
    
    def _create_roads(self):
        """Create roads connecting locations"""
        locations = Location.query.all()
        
        if len(locations) < 2:
            return
        
        road_id = 1
        created_roads = set()  # Track created connections
        
        # Create a connected road network
        for location in locations:
            # Find nearby locations to connect
            nearby_locations = self._find_nearby_locations(location, locations, max_distance=5.0)
            
            # Connect to 2-4 nearby locations
            connections = min(len(nearby_locations), random.randint(2, 4))
            
            for i in range(connections):
                target_location = nearby_locations[i]
                
                # Avoid duplicate roads
                connection_key = tuple(sorted([location.id, target_location.id]))
                if connection_key in created_roads:
                    continue
                
                created_roads.add(connection_key)
                
                # Calculate distance
                distance = self._calculate_distance(location, target_location)
                
                # Create road
                road_name = f"Road {road_id}"
                speed_limit = random.choice([30, 40, 50, 60])  # km/h
                road_type = random.choice(['street', 'avenue', 'highway'])
                
                road = Road(
                    name=road_name,
                    from_location_id=location.id,
                    to_location_id=target_location.id,
                    distance=distance,
                    speed_limit=speed_limit,
                    road_type=road_type,
                    current_traffic=1.0,
                    is_blocked=False
                )
                
                db.session.add(road)
                self.roads_data.append({
                    'id': road_id,
                    'name': road_name,
                    'from_location_id': location.id,
                    'to_location_id': target_location.id,
                    'distance': distance,
                    'speed_limit': speed_limit,
                    'road_type': road_type
                })
                
                road_id += 1
        
        db.session.commit()
    
    def _find_nearby_locations(self, location, all_locations, max_distance=5.0):
        """Find locations within max_distance of the given location"""
        nearby = []
        
        for other_location in all_locations:
            if other_location.id == location.id:
                continue
            
            distance = self._calculate_distance(location, other_location)
            if distance <= max_distance:
                nearby.append(other_location)
        
        # Sort by distance
        nearby.sort(key=lambda loc: self._calculate_distance(location, loc))
        return nearby
    
    def _calculate_distance(self, loc1, loc2):
        """Calculate Euclidean distance between two locations"""
        dx = loc1.x - loc2.x
        dy = loc1.y - loc2.y
        return (dx * dx + dy * dy) ** 0.5
    
    def _create_transit_stops(self):
        """Create transit stops at some locations"""
        transit_locations = Location.query.filter_by(type='transit').all()
        major_locations = Location.query.filter(
            Location.type.in_(['office', 'school', 'hospital', 'shop'])
        ).limit(10).all()
        
        stop_id = 1
        
        # Create stops at transit locations
        for location in transit_locations:
            stop = TransitStop(
                name=f"{location.name} - Main Stop",
                type='bus_stop',
                location_id=location.id
            )
            stop.set_routes(['Route A', 'Route B', 'Route C'])
            stop.set_schedule({
                'weekday': {'frequency': 15, 'first': '05:00', 'last': '23:00'},
                'weekend': {'frequency': 20, 'first': '06:00', 'last': '22:00'}
            })
            
            db.session.add(stop)
            stop_id += 1
        
        # Create stops at major locations
        for location in major_locations:
            if random.random() < 0.7:  # 70% chance of having a stop
                stop = TransitStop(
                    name=f"{location.name} - Stop",
                    type='bus_stop',
                    location_id=location.id
                )
                stop.set_routes([random.choice(['Route A', 'Route B', 'Route C'])])
                stop.set_schedule({
                    'weekday': {'frequency': 20, 'first': '06:00', 'last': '22:00'}
                })
                
                db.session.add(stop)
                stop_id += 1
        
        db.session.commit()
    
    def _create_sample_agents(self):
        """Create sample agents with different roles"""
        locations = Location.query.all()
        
        if not locations:
            return
        
        agent_roles = [
            'student', 'software_engineer', 'teacher', 'restaurant_staff',
            'restaurant_customer', 'grocery_worker', 'grocery_shopper',
            'delivery_personnel', 'citizen', 'police_officer', 'firefighter',
            'doctor', 'nurse', 'bus_driver', 'taxi_driver'
        ]
        
        # Create agents for each role
        agent_id = 1
        
        for role in agent_roles:
            count = self._get_agent_count_for_role(role)
            
            for i in range(count):
                # Select appropriate starting location based on role
                start_location = self._select_start_location_for_role(role, locations)
                
                agent_name = f"{role.replace('_', ' ').title()} {agent_id}"
                
                agent = Agent(
                    name=agent_name,
                    role=role,
                    x=start_location.x + random.uniform(-0.1, 0.1),  # Small random offset
                    y=start_location.y + random.uniform(-0.1, 0.1),
                    status='idle',
                    energy=random.uniform(80, 100),
                    health=random.uniform(90, 100),
                    current_location_id=start_location.id
                )
                
                # Set role-specific schedule and preferences
                schedule = self._generate_schedule_for_role(role, locations)
                preferences = self._generate_preferences_for_role(role)
                
                agent.set_schedule(schedule)
                agent.set_preferences(preferences)
                
                db.session.add(agent)
                self.agents_data.append({
                    'id': agent_id,
                    'name': agent_name,
                    'role': role,
                    'x': agent.x,
                    'y': agent.y,
                    'current_location_id': start_location.id
                })
                
                agent_id += 1
        
        db.session.commit()
    
    def _get_agent_count_for_role(self, role):
        """Get number of agents to create for each role"""
        role_counts = {
            'student': 15,
            'software_engineer': 10,
            'teacher': 8,
            'restaurant_staff': 6,
            'restaurant_customer': 12,
            'grocery_worker': 4,
            'grocery_shopper': 10,
            'delivery_personnel': 8,
            'citizen': 20,
            'police_officer': 4,
            'firefighter': 3,
            'doctor': 5,
            'nurse': 6,
            'bus_driver': 4,
            'taxi_driver': 6
        }
        
        return role_counts.get(role, 5)
    
    def _select_start_location_for_role(self, role, locations):
        """Select appropriate starting location for agent role"""
        role_location_preferences = {
            'student': ['school', 'residential'],
            'software_engineer': ['office', 'residential'],
            'teacher': ['school', 'residential'],
            'restaurant_staff': ['restaurant'],
            'restaurant_customer': ['residential', 'restaurant'],
            'grocery_worker': ['shop'],
            'grocery_shopper': ['residential', 'shop'],
            'delivery_personnel': ['transit', 'shop'],
            'citizen': ['residential', 'park'],
            'police_officer': ['office', 'transit'],
            'firefighter': ['office'],
            'doctor': ['hospital'],
            'nurse': ['hospital'],
            'bus_driver': ['transit'],
            'taxi_driver': ['transit', 'residential']
        }
        
        preferred_types = role_location_preferences.get(role, ['residential'])
        
        # Find locations of preferred types
        suitable_locations = [loc for loc in locations if loc.type in preferred_types]
        
        if not suitable_locations:
            suitable_locations = locations
        
        return random.choice(suitable_locations)
    
    def _generate_schedule_for_role(self, role, locations):
        """Generate a basic schedule for agent role"""
        # This is a simplified schedule - the behavior system will handle detailed scheduling
        role_schedules = {
            'student': {
                '08:00-12:00': {'type': 'attending_class', 'duration': 240},
                '12:00-13:00': {'type': 'lunch', 'duration': 60},
                '13:00-17:00': {'type': 'studying', 'duration': 240}
            },
            'software_engineer': {
                '09:00-12:00': {'type': 'coding', 'duration': 180},
                '12:00-13:00': {'type': 'lunch', 'duration': 60},
                '13:00-17:00': {'type': 'meetings', 'duration': 240}
            },
            'teacher': {
                '08:30-12:00': {'type': 'teaching', 'duration': 210},
                '12:00-13:00': {'type': 'lunch', 'duration': 60},
                '13:00-16:00': {'type': 'grading', 'duration': 180}
            }
        }
        
        return role_schedules.get(role, {})
    
    def _generate_preferences_for_role(self, role):
        """Generate preferences for agent role"""
        return {
            'preferred_transport': random.choice(['walking', 'car', 'bus']),
            'activity_preference': random.choice(['indoor', 'outdoor', 'mixed']),
            'social_level': random.uniform(0.3, 1.0)
        }
    
    def _create_initial_events(self):
        """Create some initial events"""
        # Create a few sample events
        current_time = datetime.utcnow()
        
        # Morning rush hour traffic
        rush_hour_event = Event(
            name='Morning Rush Hour',
            type='traffic',
            severity='medium',
            start_time=current_time.replace(hour=7, minute=0),
            end_time=current_time.replace(hour=9, minute=0),
            description='Increased traffic during morning commute'
        )
        rush_hour_event.set_effects({
            'traffic_increase': 1.5,
            'public_transport_crowding': True
        })
        
        db.session.add(rush_hour_event)
        
        # Weekend festival (if it's weekend)
        if current_time.weekday() >= 5:  # Saturday or Sunday
            festival_event = Event(
                name='Weekend Market Festival',
                type='social',
                severity='low',
                start_time=current_time.replace(hour=10, minute=0),
                end_time=current_time.replace(hour=16, minute=0),
                description='Local market festival with food and entertainment'
            )
            festival_event.set_effects({
                'increased_foot_traffic': True,
                'location_crowding': True
            })
            
            db.session.add(festival_event)
        
        db.session.commit()
    
    def _initialize_simulation_state(self):
        """Initialize the main simulation state"""
        # Check if simulation state already exists
        existing_state = SimulationState.query.filter_by(name='main').first()
        
        if existing_state:
            # Update existing state
            existing_state.total_agents = Agent.query.count()
            existing_state.total_events = Event.query.count()
            existing_state.updated_at = datetime.utcnow()
        else:
            # Create new simulation state
            sim_state = SimulationState(
                name='main',
                is_running=False,
                current_time=datetime.utcnow(),
                time_acceleration=1.0,
                total_agents=Agent.query.count(),
                active_agents=0,
                total_events=Event.query.count(),
                active_events=0,
                weather_condition='clear',
                temperature=20.0
            )
            
            # Set default settings
            sim_state.set_settings({
                'max_agents': 1000,
                'weather_enabled': True,
                'events_enabled': True,
                'traffic_simulation': True,
                'agent_ai_enabled': True
            })
            
            # Set initial statistics
            sim_state.set_statistics({
                'total_distance_traveled': 0,
                'total_activities_completed': 0,
                'average_agent_energy': 90.0,
                'average_agent_health': 95.0
            })
            
            db.session.add(sim_state)
        
        # Initialize weather
        initial_weather = WeatherCondition(
            condition='clear',
            temperature=20.0,
            humidity=50.0,
            wind_speed=5.0,
            visibility=10.0,
            start_time=datetime.utcnow()
        )
        initial_weather.set_effects({
            'movement_modifier': 1.0,
            'energy_modifier': 1.0
        })
        
        db.session.add(initial_weather)
        db.session.commit()
    
    def get_initialization_summary(self):
        """Get summary of initialized data"""
        return {
            'locations': len(self.locations_data),
            'roads': len(self.roads_data),
            'agents': len(self.agents_data),
            'events': len(self.events_data),
            'location_types': self._count_by_type(self.locations_data, 'type'),
            'agent_roles': self._count_by_type(self.agents_data, 'role')
        }
    
    def _count_by_type(self, data_list, type_field):
        """Count items by type field"""
        counts = {}
        for item in data_list:
            item_type = item.get(type_field, 'unknown')
            counts[item_type] = counts.get(item_type, 0) + 1
        return counts

