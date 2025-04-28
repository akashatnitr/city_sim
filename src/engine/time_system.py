"""
Time system module for AI City Simulator.
Manages the simulation time.
"""
from datetime import datetime, timedelta


class TimeSystem:
    """Manages the simulation time."""
    
    def __init__(self, start_time, time_scale=60):
        """
        Initialize the time system.
        
        Args:
            start_time (datetime): Starting time for the simulation
            time_scale (float): Number of simulation seconds per real second
        """
        self.start_time = start_time
        self.current_time = start_time
        self.time_scale = time_scale
        self.elapsed_ticks = 0
    
    def update(self, speed_multiplier=1.0):
        """
        Update the simulation time.
        
        Args:
            speed_multiplier (float): Multiplier for the time scale
            
        Returns:
            datetime: The new current time
        """
        # Increment the elapsed ticks
        self.elapsed_ticks += 1
        
        # Calculate the time delta
        delta_seconds = self.time_scale * speed_multiplier
        
        # Update the current time
        self.current_time += timedelta(seconds=delta_seconds)
        
        return self.current_time
    
    def get_time(self):
        """
        Get the current simulation time.
        
        Returns:
            datetime: Current simulation time
        """
        return self.current_time
    
    def get_time_str(self):
        """
        Get a string representation of the current simulation time.
        
        Returns:
            str: Current simulation time as a string
        """
        return self.current_time.strftime("%A, %B %d, %Y - %I:%M %p")
    
    def get_day_phase(self):
        """
        Get the current phase of the day.
        
        Returns:
            str: Current phase of the day (morning, afternoon, evening, night)
        """
        hour = self.current_time.hour
        
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def get_elapsed_days(self):
        """
        Get the number of days elapsed since the start of the simulation.
        
        Returns:
            int: Number of days elapsed
        """
        delta = self.current_time - self.start_time
        return delta.days
    
    def get_elapsed_hours(self):
        """
        Get the number of hours elapsed since the start of the simulation.
        
        Returns:
            float: Number of hours elapsed
        """
        delta = self.current_time - self.start_time
        return delta.total_seconds() / 3600
    
    def get_elapsed_minutes(self):
        """
        Get the number of minutes elapsed since the start of the simulation.
        
        Returns:
            float: Number of minutes elapsed
        """
        delta = self.current_time - self.start_time
        return delta.total_seconds() / 60
