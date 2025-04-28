"""
Need module for AI City Simulator.
Defines needs that agents must satisfy.
"""


class Need:
    """Represents a need that an agent must satisfy."""
    
    def __init__(self, name, value=100, decay_rate=0.1):
        """
        Initialize a need.
        
        Args:
            name (str): Name of the need
            value (float): Initial value of the need (0-100)
            decay_rate (float): Rate at which the need decays per tick
        """
        self.name = name
        self.value = value
        self.decay_rate = decay_rate
    
    def update(self):
        """
        Update the need value based on decay rate.
        
        Returns:
            float: New value of the need
        """
        self.value = max(0, self.value - self.decay_rate)
        return self.value
    
    def satisfy(self, amount):
        """
        Satisfy the need by a certain amount.
        
        Args:
            amount (float): Amount to increase the need value by
            
        Returns:
            float: New value of the need
        """
        self.value = min(100, self.value + amount)
        return self.value
    
    def is_critical(self, threshold=20):
        """
        Check if the need is at a critical level.
        
        Args:
            threshold (float): Threshold below which the need is critical
            
        Returns:
            bool: True if the need is critical, False otherwise
        """
        return self.value <= threshold
    
    def is_satisfied(self, threshold=80):
        """
        Check if the need is satisfied.
        
        Args:
            threshold (float): Threshold above which the need is satisfied
            
        Returns:
            bool: True if the need is satisfied, False otherwise
        """
        return self.value >= threshold
    
    def __str__(self):
        """String representation of the need."""
        return f"{self.name}: {self.value:.1f}"
