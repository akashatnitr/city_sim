"""
Simulation engine for AI City Simulator.
Manages the overall simulation state, time, and coordinates between agents and the city.
"""
import time
import random
from datetime import datetime, timedelta

from src.engine.city import City
from src.engine.time_system import TimeSystem
from src.engine.weather_system import WeatherSystem
from src.engine.crime_system import CrimeSystem
from src.engine.traffic_system import TrafficSystem
from src.engine.event_system import EventSystem
from src.agents.agent_manager import AgentManager


class Simulation:
    """Main simulation class that coordinates all simulation systems."""
    
    def __init__(self, config):
        """
        Initialize the simulation with the given configuration.
        
        Args:
            config (dict): Configuration dictionary
        """
        self.config = config
        self.paused = False
        self.speed = 1.0  # Simulation speed multiplier
        
        # Initialize simulation time (starts at 8:00 AM by default)
        start_hour = config.get('start_hour', 8)
        self.time_system = TimeSystem(
            datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0),
            time_scale=config.get('time_scale', 60)  # 1 second real time = 1 minute sim time by default
        )
        
        # Initialize city
        self.city = City(config.get('city', {}))
        
        # Initialize agent manager
        self.agent_manager = AgentManager(self, config.get('agents', {}))
        
        # Initialize systems
        self.weather_system = WeatherSystem(self, config.get('weather', {}))
        self.crime_system = CrimeSystem(self, config.get('crime', {}))
        self.traffic_system = TrafficSystem(self, config.get('traffic', {}))
        self.event_system = EventSystem(self, config.get('events', {}))
        
        # Statistics tracking
        self.stats = {
            'tick_count': 0,
            'start_time': time.time(),
            'crimes': 0,
            'traffic_jams': 0,
            'special_events': 0,
        }
    
    def update(self):
        """Update the simulation state by one tick."""
        # Update simulation time
        self.time_system.update(self.speed)
        
        # Update systems
        self.weather_system.update()
        self.traffic_system.update()
        self.crime_system.update()
        self.event_system.update()
        
        # Update city
        self.city.update(self.time_system.get_time())
        
        # Update agents
        self.agent_manager.update()
        
        # Update statistics
        self.stats['tick_count'] += 1
        
        # Occasionally trigger city growth if enabled
        if self.config.get('enable_city_growth', True) and random.random() < 0.001 * self.speed:
            self.city.grow()
    
    def toggle_pause(self):
        """Toggle the pause state of the simulation."""
        self.paused = not self.paused
        return self.paused
    
    def increase_speed(self):
        """Increase the simulation speed."""
        self.speed = min(self.speed * 2, 16.0)
        print(f"Simulation speed: {self.speed}x")
        return self.speed
    
    def decrease_speed(self):
        """Decrease the simulation speed."""
        self.speed = max(self.speed / 2, 0.25)
        print(f"Simulation speed: {self.speed}x")
        return self.speed
    
    def get_time(self):
        """Get the current simulation time."""
        return self.time_system.get_time()
    
    def get_time_str(self):
        """Get a string representation of the current simulation time."""
        return self.time_system.get_time_str()
    
    def get_day_phase(self):
        """Get the current phase of the day (morning, afternoon, evening, night)."""
        return self.time_system.get_day_phase()
    
    def get_statistics(self):
        """Get simulation statistics."""
        stats = self.stats.copy()
        stats['elapsed_real_time'] = time.time() - stats['start_time']
        stats['sim_time'] = self.get_time_str()
        stats['agent_count'] = self.agent_manager.get_agent_count()
        stats['weather'] = self.weather_system.get_current_weather()
        return stats
