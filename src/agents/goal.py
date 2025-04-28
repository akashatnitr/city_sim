"""
Goal module for AI City Simulator.
Defines goals that agents can pursue.
"""


class Goal:
    """Represents a goal that an agent can pursue."""
    
    def __init__(self, name, timeframe, priority):
        """
        Initialize a goal.
        
        Args:
            name (str): Name of the goal
            timeframe (str): Timeframe of the goal (short_term, medium_term, long_term)
            priority (int): Priority of the goal (0-100)
        """
        self.name = name
        self.timeframe = timeframe
        self.priority = priority
        self.progress = 0  # Progress towards the goal (0-100)
        self.active = True  # Whether the goal is currently being pursued
    
    def update_progress(self, amount):
        """
        Update the progress towards the goal.
        
        Args:
            amount (int): Amount to increase progress by
            
        Returns:
            bool: True if the goal is now complete, False otherwise
        """
        self.progress = min(100, self.progress + amount)
        return self.progress >= 100
    
    def is_complete(self):
        """
        Check if the goal is complete.
        
        Returns:
            bool: True if the goal is complete, False otherwise
        """
        return self.progress >= 100
    
    def adjust_priority(self, amount):
        """
        Adjust the priority of the goal.
        
        Args:
            amount (int): Amount to adjust priority by
        """
        self.priority = max(0, min(100, self.priority + amount))
    
    def __str__(self):
        """String representation of the goal."""
        return f"{self.name} ({self.progress}% complete, priority: {self.priority})"
