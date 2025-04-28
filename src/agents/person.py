"""
Person module for AI City Simulator.
Represents individual agents in the city.
"""
import random
import math
from datetime import datetime, timedelta

from src.agents.goal import Goal
from src.agents.need import Need


class Person:
    """Represents a person (agent) in the city."""
    
    def __init__(self, name, age, gender, agent_type, personality, initial_location, simulation):
        """
        Initialize a person.
        
        Args:
            name (str): Name of the person
            age (int): Age of the person
            gender (str): Gender of the person
            agent_type (str): Type of agent (resident, worker, etc.)
            personality: Personality traits
            initial_location: Starting location
            simulation: The simulation instance
        """
        self.name = name
        self.age = age
        self.gender = gender
        self.agent_type = agent_type
        self.personality = personality
        self.simulation = simulation
        
        # Position and movement
        self.current_location = initial_location
        self.x = initial_location.x
        self.y = initial_location.y
        self.target_x = self.x
        self.target_y = self.y
        self.speed = 2.0  # Units per tick
        self.path = []
        self.moving = False
        self.transportation_mode = 'walking'  # walking, driving, bus
        
        # Current state
        self.state = 'idle'  # idle, moving, working, shopping, etc.
        self.current_activity = None
        self.activity_start_time = None
        self.activity_duration = 0
        
        # Needs (0-100)
        self.needs = {
            'energy': Need('energy', 100, 0.1),  # Decreases over time, restored by sleeping
            'hunger': Need('hunger', 100, 0.2),  # Decreases over time, restored by eating
            'social': Need('social', 100, 0.05),  # Decreases over time, restored by socializing
            'hygiene': Need('hygiene', 100, 0.1),  # Decreases over time, restored by showering
            'fun': Need('fun', 100, 0.1),  # Decreases over time, restored by entertainment
            'money': Need('money', 50, 0),  # Doesn't decrease over time, gained by working
        }
        
        # Goals
        self.goals = []
        self._generate_initial_goals()
        
        # Schedule
        self.schedule = self._generate_schedule()
        
        # Memory and knowledge
        self.memory = []
        self.known_locations = [initial_location]
        
        # Relationships
        self.relationships = {}  # Person -> relationship value (-100 to 100)
        
        # Stats
        self.stats = {
            'crimes_committed': 0,
            'money_earned': 0,
            'distance_traveled': 0,
            'meals_eaten': 0,
            'social_interactions': 0,
        }
    
    def _generate_initial_goals(self):
        """Generate initial goals based on agent type."""
        if self.agent_type == 'resident':
            self.goals.append(Goal('Find a job', 'long_term', 50))
            self.goals.append(Goal('Make friends', 'long_term', 30))
            
            if random.random() < 0.3:
                self.goals.append(Goal('Start a business', 'long_term', 70))
            
        elif self.agent_type == 'worker':
            self.goals.append(Goal('Get a promotion', 'long_term', 60))
            self.goals.append(Goal('Save money', 'long_term', 50))
            
        elif self.agent_type == 'student':
            self.goals.append(Goal('Graduate', 'long_term', 80))
            self.goals.append(Goal('Make friends', 'long_term', 40))
            
            if self.age > 16:
                self.goals.append(Goal('Get a part-time job', 'medium_term', 30))
            
        elif self.agent_type == 'police':
            self.goals.append(Goal('Maintain order', 'long_term', 70))
            self.goals.append(Goal('Catch criminals', 'medium_term', 60))
            
        elif self.agent_type == 'criminal':
            self.goals.append(Goal('Make money illegally', 'medium_term', 70))
            self.goals.append(Goal('Avoid getting caught', 'long_term', 90))
            
        elif self.agent_type == 'visitor':
            self.goals.append(Goal('See the sights', 'short_term', 80))
            self.goals.append(Goal('Have fun', 'short_term', 70))
            
        # Add some universal goals
        if random.random() < 0.5:
            self.goals.append(Goal('Stay healthy', 'long_term', 40))
        
        if random.random() < 0.3:
            self.goals.append(Goal('Find love', 'long_term', 50))
    
    def _generate_schedule(self):
        """Generate a daily schedule based on agent type."""
        schedule = {}
        
        # Default schedule for all agents
        schedule['sleep'] = {'start': '22:00', 'end': '06:00', 'location_type': 'residential'}
        schedule['breakfast'] = {'start': '07:00', 'end': '08:00', 'location_type': 'residential'}
        schedule['dinner'] = {'start': '18:00', 'end': '19:00', 'location_type': 'residential'}
        
        # Agent-specific schedules
        if self.agent_type == 'resident':
            schedule['free_time'] = {'start': '10:00', 'end': '16:00', 'location_type': 'any'}
            
        elif self.agent_type == 'worker':
            schedule['work'] = {'start': '09:00', 'end': '17:00', 'location_type': 'commercial'}
            
        elif self.agent_type == 'student':
            if self.age < 14:  # Elementary/middle school
                schedule['school'] = {'start': '08:30', 'end': '15:00', 'location_type': 'Elementary School'}
            elif self.age < 18:  # High school
                schedule['school'] = {'start': '08:00', 'end': '15:30', 'location_type': 'High School'}
            else:  # College
                schedule['school'] = {'start': '09:00', 'end': '16:00', 'location_type': 'College'}
            
        elif self.agent_type == 'police':
            # Police work in shifts
            shift = random.choice(['morning', 'afternoon', 'night'])
            if shift == 'morning':
                schedule['work'] = {'start': '06:00', 'end': '14:00', 'location_type': 'Police Station'}
            elif shift == 'afternoon':
                schedule['work'] = {'start': '14:00', 'end': '22:00', 'location_type': 'Police Station'}
            else:  # night
                schedule['work'] = {'start': '22:00', 'end': '06:00', 'location_type': 'Police Station'}
                # Adjust sleep schedule for night shift
                schedule['sleep'] = {'start': '10:00', 'end': '18:00', 'location_type': 'residential'}
            
        elif self.agent_type == 'criminal':
            # Criminals are more active at night
            schedule['criminal_activity'] = {'start': '23:00', 'end': '03:00', 'location_type': 'any'}
            
        elif self.agent_type == 'visitor':
            schedule['sightseeing'] = {'start': '10:00', 'end': '16:00', 'location_type': 'any'}
        
        return schedule
    
    def update(self):
        """Update the agent's state for the current tick."""
        # Update needs
        for need in self.needs.values():
            need.update()
        
        # Check if we need to change activity based on schedule
        self._check_schedule()
        
        # If we're moving, continue movement
        if self.moving:
            self._update_movement()
        else:
            # If we're not moving, decide what to do
            self._decide_next_action()
    
    def _check_schedule(self):
        """Check if we need to start a scheduled activity."""
        current_time = self.simulation.get_time()
        current_time_str = current_time.strftime('%H:%M')
        
        # Check each scheduled activity
        for activity, details in self.schedule.items():
            start_time = details['start']
            end_time = details['end']
            
            # Check if it's time to start this activity
            if start_time <= current_time_str < end_time:
                # If we're not already doing this activity, start it
                if self.current_activity != activity:
                    self._start_activity(activity, details)
                    return
    
    def _start_activity(self, activity, details):
        """Start a new activity."""
        self.current_activity = activity
        self.activity_start_time = self.simulation.get_time()
        
        # Find an appropriate location for this activity
        location_type = details.get('location_type', 'any')
        
        if location_type == 'any':
            # Choose a random location
            target_location = random.choice(self.simulation.city.get_all_locations())
        elif location_type == 'residential':
            # For residential activities, prefer home
            residential_locations = self.simulation.city.get_locations_by_category('residential')
            if residential_locations:
                # Try to find a consistent "home" for this agent
                home_locations = [loc for loc in residential_locations 
                                 if loc.name.endswith(str(hash(self.name) % 1000))]
                if home_locations:
                    target_location = home_locations[0]
                else:
                    target_location = random.choice(residential_locations)
            else:
                target_location = random.choice(self.simulation.city.get_all_locations())
        else:
            # Find locations of the specified type
            locations = self.simulation.city.get_locations_by_type(location_type)
            if not locations:
                # If no locations of that type, try by category
                locations = self.simulation.city.get_locations_by_category(location_type)
            
            if locations:
                target_location = random.choice(locations)
            else:
                # Fallback to any location
                target_location = random.choice(self.simulation.city.get_all_locations())
        
        # Move to the target location
        self.move_to_location(target_location)
    
    def move_to_location(self, target_location):
        """
        Start moving to a target location.
        
        Args:
            target_location: The location to move to
        """
        # Set target coordinates
        self.target_x = target_location.x
        self.target_y = target_location.y
        
        # Find a path to the target
        self.path = self.simulation.city.road_network.find_path(
            self.x, self.y, self.target_x, self.target_y
        )
        
        # Start moving
        self.moving = True
        self.state = 'moving'
        
        # Choose transportation mode
        distance = ((self.target_x - self.x) ** 2 + (self.target_y - self.y) ** 2) ** 0.5
        
        if distance > 500:
            # Long distance, try to take a bus
            nearest_bus_stop = self.simulation.city.road_network.get_nearest_bus_stop(self.x, self.y)
            if nearest_bus_stop and random.random() < 0.7:
                self.transportation_mode = 'bus'
                self.speed = 5.0
            else:
                # No bus available, drive
                self.transportation_mode = 'driving'
                self.speed = 4.0
        elif distance > 200:
            # Medium distance, drive
            self.transportation_mode = 'driving'
            self.speed = 4.0
        else:
            # Short distance, walk
            self.transportation_mode = 'walking'
            self.speed = 2.0
    
    def _update_movement(self):
        """Update the agent's position while moving."""
        if not self.path:
            # If we've reached the end of the path, stop moving
            self.moving = False
            self.state = 'idle'
            return
        
        # Get the next point in the path
        next_x, next_y = self.path[0]
        
        # Calculate direction and distance to the next point
        dx = next_x - self.x
        dy = next_y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance <= self.speed:
            # We've reached this point, move to the next one
            self.x = next_x
            self.y = next_y
            self.path.pop(0)
            
            # Update stats
            self.stats['distance_traveled'] += distance
        else:
            # Move towards the next point
            direction_x = dx / distance
            direction_y = dy / distance
            
            self.x += direction_x * self.speed
            self.y += direction_y * self.speed
            
            # Update stats
            self.stats['distance_traveled'] += self.speed
        
        # Check if we've reached the target
        if not self.path and abs(self.x - self.target_x) < 5 and abs(self.y - self.target_y) < 5:
            # We've reached the target
            self.moving = False
            self.state = 'idle'
            
            # Find the location we've reached
            target_location = self.simulation.city.get_nearest_location(self.x, self.y)
            
            if target_location:
                # Leave current location
                if self.current_location:
                    self.current_location.remove_agent(self)
                
                # Enter new location
                target_location.add_agent(self)
                self.current_location = target_location
                
                # Add to known locations if not already known
                if target_location not in self.known_locations:
                    self.known_locations.append(target_location)
    
    def _decide_next_action(self):
        """Decide what action to take next based on needs and goals."""
        # If we're already doing an activity, continue it
        if self.current_activity:
            return
        
        # Check if any needs are critical
        critical_needs = [need for need in self.needs.values() if need.value < 20]
        
        if critical_needs:
            # Address the most critical need
            critical_need = min(critical_needs, key=lambda n: n.value)
            self._address_need(critical_need)
            return
        
        # If no critical needs, check goals
        if self.goals:
            # Sort goals by priority
            sorted_goals = sorted(self.goals, key=lambda g: g.priority, reverse=True)
            
            # Try to address the highest priority goal
            self._address_goal(sorted_goals[0])
            return
        
        # If no critical needs or goals, do something random
        self._do_random_activity()
    
    def _address_need(self, need):
        """
        Address a specific need.
        
        Args:
            need: The need to address
        """
        if need.name == 'energy':
            # Find a place to sleep
            self._start_activity('sleep', {'location_type': 'residential'})
            
        elif need.name == 'hunger':
            # Find a place to eat
            if random.random() < 0.3:
                # Eat at a restaurant
                self._start_activity('eat', {'location_type': 'Restaurant'})
            else:
                # Eat at home
                self._start_activity('eat', {'location_type': 'residential'})
            
        elif need.name == 'social':
            # Find a place to socialize
            if random.random() < 0.5:
                # Socialize at a public place
                location_type = random.choice(['Restaurant', 'Coffee Shop', 'Bar', 'Park'])
                self._start_activity('socialize', {'location_type': location_type})
            else:
                # Socialize at home
                self._start_activity('socialize', {'location_type': 'residential'})
            
        elif need.name == 'hygiene':
            # Take care of hygiene at home
            self._start_activity('hygiene', {'location_type': 'residential'})
            
        elif need.name == 'fun':
            # Find a fun activity
            location_type = random.choice(['Movie Theater', 'Park', 'Bar', 'Gym'])
            self._start_activity('fun', {'location_type': location_type})
            
        elif need.name == 'money':
            # Find a way to make money
            if self.agent_type == 'criminal':
                # Criminals make money through crime
                self._start_activity('criminal_activity', {'location_type': 'any'})
            else:
                # Others work at jobs
                self._start_activity('work', {'location_type': 'commercial'})
    
    def _address_goal(self, goal):
        """
        Take action to address a specific goal.
        
        Args:
            goal: The goal to address
        """
        # Different actions based on goal name
        if goal.name == 'Find a job':
            # Look for job opportunities
            self._start_activity('job_hunting', {'location_type': 'commercial'})
            
        elif goal.name == 'Make friends':
            # Go to social places
            location_type = random.choice(['Restaurant', 'Coffee Shop', 'Bar', 'Park'])
            self._start_activity('socialize', {'location_type': location_type})
            
        elif goal.name == 'Start a business':
            # Research and plan business
            location_type = random.choice(['Coffee Shop', 'Library'])
            self._start_activity('business_planning', {'location_type': location_type})
            
        elif goal.name == 'Get a promotion':
            # Work hard
            self._start_activity('work', {'location_type': 'commercial'})
            
        elif goal.name == 'Save money':
            # Avoid spending money
            self._start_activity('free_activity', {'location_type': 'Park'})
            
        elif goal.name == 'Graduate':
            # Study
            if self.age < 18:
                self._start_activity('study', {'location_type': 'Library'})
            else:
                self._start_activity('study', {'location_type': 'College'})
            
        elif goal.name == 'Maintain order':
            # Patrol the city
            self._start_activity('patrol', {'location_type': 'any'})
            
        elif goal.name == 'Catch criminals':
            # Look for criminal activity
            criminal_hotspots = ['Bar', 'Park', 'Shopping Mall']
            location_type = random.choice(criminal_hotspots)
            self._start_activity('investigate', {'location_type': location_type})
            
        elif goal.name == 'Make money illegally':
            # Find targets for crime
            targets = ['Shopping Mall', 'House', 'Apartment']
            location_type = random.choice(targets)
            self._start_activity('criminal_activity', {'location_type': location_type})
            
        elif goal.name == 'Avoid getting caught':
            # Lay low
            self._start_activity('hide', {'location_type': 'residential'})
            
        elif goal.name == 'See the sights':
            # Visit tourist attractions
            attractions = ['Park', 'Museum', 'Shopping Mall']
            location_type = random.choice(attractions)
            self._start_activity('sightseeing', {'location_type': location_type})
            
        elif goal.name == 'Have fun':
            # Do something fun
            fun_places = ['Movie Theater', 'Bar', 'Restaurant', 'Park']
            location_type = random.choice(fun_places)
            self._start_activity('fun', {'location_type': location_type})
            
        elif goal.name == 'Stay healthy':
            # Exercise
            self._start_activity('exercise', {'location_type': 'Gym'})
            
        elif goal.name == 'Find love':
            # Go to social places
            location_type = random.choice(['Restaurant', 'Coffee Shop', 'Bar', 'Park'])
            self._start_activity('dating', {'location_type': location_type})
        
        else:
            # Default behavior for unknown goals
            self._do_random_activity()
    
    def _do_random_activity(self):
        """Choose a random activity to do."""
        activities = [
            ('relax', {'location_type': 'residential'}),
            ('shop', {'location_type': 'Grocery Store'}),
            ('exercise', {'location_type': 'Gym'}),
            ('socialize', {'location_type': 'Coffee Shop'}),
            ('entertainment', {'location_type': 'Movie Theater'}),
            ('walk', {'location_type': 'Park'})
        ]
        
        activity, details = random.choice(activities)
        self._start_activity(activity, details)
    
    def get_color(self):
        """Get the color representing this agent's type."""
        colors = {
            'resident': (0, 0, 255),    # Blue
            'worker': (0, 255, 0),      # Green
            'student': (255, 255, 0),   # Yellow
            'police': (0, 0, 128),      # Dark blue
            'criminal': (255, 0, 0),    # Red
            'visitor': (255, 0, 255)    # Magenta
        }
        
        return colors.get(self.agent_type, (128, 128, 128))  # Default gray
    
    def get_info(self):
        """Get information about this agent for display."""
        return {
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'type': self.agent_type,
            'location': str(self.current_location) if self.current_location else "Unknown",
            'activity': self.current_activity or "None",
            'state': self.state,
            'transportation': self.transportation_mode,
            'needs': {name: need.value for name, need in self.needs.items()},
            'goals': [{'name': goal.name, 'priority': goal.priority} for goal in self.goals],
            'stats': self.stats
        }
    
    def __str__(self):
        """String representation of the agent."""
        return f"{self.name} ({self.age}, {self.agent_type})"
