import threading
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.models.agent import Agent, AgentMovement, AgentActivity
from src.models.location import Location, Road
from src.models.event import SimulationState, Event, WeatherCondition, SimulationLog
from src.models.user import db
from src.simulation.agent_behaviors import AgentBehaviorManager
from src.simulation.pathfinding import PathfindingSystem
from src.simulation.weather_system import WeatherSystem
from src.simulation.event_manager import EventManager

class SimulationEngine:
    def __init__(self, socketio):
        self.socketio = socketio
        self.is_running = False
        self.simulation_thread = None
        self.agents = {}  # agent_id -> agent data
        self.locations = {}  # location_id -> location data
        self.roads = {}  # road_id -> road data
        self.current_time = datetime.utcnow()
        self.time_acceleration = 1.0
        self.tick_rate = 1.0  # seconds per simulation tick
        
        # Initialize subsystems
        self.behavior_manager = AgentBehaviorManager(self)
        self.pathfinding = PathfindingSystem(self)
        self.weather_system = WeatherSystem(self)
        self.event_manager = EventManager(self)
        
        # Statistics
        self.stats = {
            'total_ticks': 0,
            'agents_moved': 0,
            'activities_completed': 0,
            'events_triggered': 0
        }

    def start_simulation(self, config=None):
        """Start the simulation with optional configuration"""
        if self.is_running:
            return
        
        self.is_running = True
        if config:
            self.time_acceleration = config.get('time_acceleration', 1.0)
            self.tick_rate = config.get('tick_rate', 1.0)
        
        # Load initial data
        self.load_simulation_data()
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        self.log_event('system', 'simulation_started', {'config': config})
        self.emit_update('simulation_started', {'time_acceleration': self.time_acceleration})

    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5.0)
        
        self.log_event('system', 'simulation_stopped', {})
        self.emit_update('simulation_stopped', {})

    def load_simulation_data(self):
        """Load agents, locations, and roads from database"""
        try:
            # Load agents
            agents = Agent.query.all()
            for agent in agents:
                self.agents[agent.id] = agent.to_dict()
            
            # Load locations
            locations = Location.query.all()
            for location in locations:
                self.locations[location.id] = location.to_dict()
            
            # Load roads
            roads = Road.query.all()
            for road in roads:
                self.roads[road.id] = road.to_dict()
            
            print(f"Loaded {len(self.agents)} agents, {len(self.locations)} locations, {len(self.roads)} roads")
        except Exception as e:
            print(f"Error loading simulation data: {e}")

    def _simulation_loop(self):
        """Main simulation loop"""
        last_tick = time.time()
        
        while self.is_running:
            current_real_time = time.time()
            
            # Calculate simulation time advancement
            real_time_delta = current_real_time - last_tick
            sim_time_delta = real_time_delta * self.time_acceleration
            self.current_time += timedelta(seconds=sim_time_delta)
            
            # Process simulation tick
            self._process_tick()
            
            # Update statistics
            self.stats['total_ticks'] += 1
            
            # Emit periodic updates
            if self.stats['total_ticks'] % 10 == 0:  # Every 10 ticks
                self._emit_periodic_update()
            
            last_tick = current_real_time
            
            # Sleep to maintain tick rate
            time.sleep(self.tick_rate)

    def _process_tick(self):
        """Process one simulation tick"""
        try:
            # Update weather
            self.weather_system.update(self.current_time)
            
            # Process events
            self.event_manager.process_events(self.current_time)
            
            # Update all agents
            for agent_id, agent_data in self.agents.items():
                self._update_agent(agent_id, agent_data)
            
            # Update locations
            self._update_locations()
            
        except Exception as e:
            print(f"Error in simulation tick: {e}")

    def _update_agent(self, agent_id, agent_data):
        """Update a single agent's state"""
        try:
            # Get agent behavior
            behavior = self.behavior_manager.get_behavior(agent_data['role'])
            
            # Update agent based on current activity and schedule
            new_action = behavior.update(agent_data, self.current_time)
            
            if new_action:
                self._execute_agent_action(agent_id, agent_data, new_action)
            
            # Update agent energy and health
            self._update_agent_vitals(agent_data)
            
        except Exception as e:
            print(f"Error updating agent {agent_id}: {e}")

    def _execute_agent_action(self, agent_id, agent_data, action):
        """Execute an agent action"""
        action_type = action.get('type')
        
        if action_type == 'move':
            self._move_agent(agent_id, agent_data, action)
        elif action_type == 'activity':
            self._start_agent_activity(agent_id, agent_data, action)
        elif action_type == 'wait':
            agent_data['status'] = 'waiting'

    def _move_agent(self, agent_id, agent_data, move_action):
        """Move an agent to a new location"""
        target_location_id = move_action.get('target_location_id')
        target_x = move_action.get('target_x', agent_data['x'])
        target_y = move_action.get('target_y', agent_data['y'])
        
        # Calculate path if needed
        if target_location_id and target_location_id in self.locations:
            target_location = self.locations[target_location_id]
            target_x = target_location['x']
            target_y = target_location['y']
        
        # Simple movement (can be enhanced with pathfinding)
        current_x, current_y = agent_data['x'], agent_data['y']
        distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
        
        if distance > 0:
            # Move towards target (simplified movement)
            speed = self._get_agent_speed(agent_data, move_action.get('transport_mode', 'walking'))
            max_distance = speed * (self.tick_rate * self.time_acceleration) / 3600  # Convert to appropriate units
            
            if distance <= max_distance:
                # Reached destination
                agent_data['x'] = target_x
                agent_data['y'] = target_y
                agent_data['status'] = 'idle'
                agent_data['current_location_id'] = target_location_id
                self.stats['agents_moved'] += 1
            else:
                # Move towards destination
                ratio = max_distance / distance
                agent_data['x'] += (target_x - current_x) * ratio
                agent_data['y'] += (target_y - current_y) * ratio
                agent_data['status'] = 'moving'

    def _start_agent_activity(self, agent_id, agent_data, activity_action):
        """Start an activity for an agent"""
        activity_type = activity_action.get('activity_type')
        duration = activity_action.get('duration', 60)  # minutes
        
        agent_data['status'] = activity_type
        agent_data['activity_start_time'] = self.current_time.isoformat()
        agent_data['activity_duration'] = duration

    def _update_agent_vitals(self, agent_data):
        """Update agent energy and health"""
        # Energy decreases over time and with activities
        energy_decay = 0.1 * (self.tick_rate * self.time_acceleration) / 3600  # per hour
        agent_data['energy'] = max(0, agent_data['energy'] - energy_decay)
        
        # Health is affected by energy and weather
        if agent_data['energy'] < 20:
            health_decay = 0.05 * (self.tick_rate * self.time_acceleration) / 3600
            agent_data['health'] = max(0, agent_data['health'] - health_decay)

    def _update_locations(self):
        """Update location occupancy and status"""
        # Reset occupancy counts
        for location_data in self.locations.values():
            location_data['current_occupancy'] = 0
        
        # Count agents at each location
        for agent_data in self.agents.values():
            location_id = agent_data.get('current_location_id')
            if location_id and location_id in self.locations:
                self.locations[location_id]['current_occupancy'] += 1

    def _get_agent_speed(self, agent_data, transport_mode):
        """Get agent movement speed based on transport mode and conditions"""
        base_speeds = {
            'walking': 5.0,  # km/h
            'cycling': 15.0,
            'car': 50.0,
            'bus': 40.0,
            'metro': 80.0
        }
        
        speed = base_speeds.get(transport_mode, 5.0)
        
        # Apply weather effects
        weather_modifier = self.weather_system.get_movement_modifier()
        speed *= weather_modifier
        
        # Apply energy effects
        if agent_data['energy'] < 50:
            speed *= 0.8
        
        return speed

    def _emit_periodic_update(self):
        """Emit periodic updates to connected clients"""
        update_data = {
            'current_time': self.current_time.isoformat(),
            'agents': list(self.agents.values()),
            'locations': list(self.locations.values()),
            'weather': self.weather_system.get_current_weather(),
            'statistics': self.stats
        }
        
        self.emit_update('simulation_update', update_data)

    def add_agent(self, agent_data):
        """Add a new agent to the simulation"""
        agent_id = agent_data.get('id')
        if agent_id:
            self.agents[agent_id] = agent_data
            self.emit_update('agent_added', agent_data)

    def remove_agent(self, agent_id):
        """Remove an agent from the simulation"""
        if agent_id in self.agents:
            agent_data = self.agents.pop(agent_id)
            self.emit_update('agent_removed', {'id': agent_id})

    def add_location(self, location_data):
        """Add a new location to the simulation"""
        location_id = location_data.get('id')
        if location_id:
            self.locations[location_id] = location_data

    def trigger_event(self, event_data):
        """Trigger a new event in the simulation"""
        self.event_manager.add_event(event_data)
        self.stats['events_triggered'] += 1

    def emit_update(self, event_name, data):
        """Emit update to connected WebSocket clients"""
        if self.socketio:
            self.socketio.emit(event_name, data)

    def log_event(self, entity_type, action, details):
        """Log a simulation event"""
        try:
            # This would normally save to database, but for now just print
            print(f"[{self.current_time}] {entity_type}: {action} - {details}")
        except Exception as e:
            print(f"Error logging event: {e}")

    def get_simulation_state(self):
        """Get current simulation state"""
        return {
            'is_running': self.is_running,
            'current_time': self.current_time.isoformat(),
            'time_acceleration': self.time_acceleration,
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if a['status'] != 'idle']),
            'statistics': self.stats,
            'weather': self.weather_system.get_current_weather()
        }

