"""
Personality module for AI City Simulator.
Defines personality traits for agents.
"""
import random


class Personality:
    """Represents a personality with various traits."""
    
    def __init__(self, traits):
        """
        Initialize a personality with traits.
        
        Args:
            traits (dict): Dictionary of trait name -> value (0-100)
        """
        self.traits = traits
    
    @classmethod
    def generate_random(cls):
        """
        Generate a random personality.
        
        Returns:
            Personality: A new personality with random traits
        """
        traits = {
            'extroversion': random.randint(0, 100),    # Sociability
            'agreeableness': random.randint(0, 100),   # Friendliness
            'conscientiousness': random.randint(0, 100),  # Work ethic
            'neuroticism': random.randint(0, 100),     # Emotional stability
            'openness': random.randint(0, 100),        # Creativity and curiosity
            'risk_taking': random.randint(0, 100),     # Willingness to take risks
            'ambition': random.randint(0, 100),        # Drive to succeed
            'empathy': random.randint(0, 100),         # Understanding of others
            'patience': random.randint(0, 100),        # Ability to wait
            'honesty': random.randint(0, 100),         # Truthfulness
        }
        
        return cls(traits)
    
    def get_trait(self, trait_name):
        """
        Get the value of a specific trait.
        
        Args:
            trait_name (str): Name of the trait
            
        Returns:
            int: Value of the trait (0-100), or 50 if trait not found
        """
        return self.traits.get(trait_name, 50)
    
    def is_trait_high(self, trait_name, threshold=70):
        """
        Check if a trait is above a threshold.
        
        Args:
            trait_name (str): Name of the trait
            threshold (int): Threshold value (default 70)
            
        Returns:
            bool: True if trait is above threshold, False otherwise
        """
        return self.get_trait(trait_name) >= threshold
    
    def is_trait_low(self, trait_name, threshold=30):
        """
        Check if a trait is below a threshold.
        
        Args:
            trait_name (str): Name of the trait
            threshold (int): Threshold value (default 30)
            
        Returns:
            bool: True if trait is below threshold, False otherwise
        """
        return self.get_trait(trait_name) <= threshold
    
    def get_description(self):
        """
        Get a text description of the personality.
        
        Returns:
            str: Description of the personality
        """
        description = []
        
        if self.is_trait_high('extroversion'):
            description.append("outgoing")
        elif self.is_trait_low('extroversion'):
            description.append("shy")
        
        if self.is_trait_high('agreeableness'):
            description.append("friendly")
        elif self.is_trait_low('agreeableness'):
            description.append("disagreeable")
        
        if self.is_trait_high('conscientiousness'):
            description.append("hardworking")
        elif self.is_trait_low('conscientiousness'):
            description.append("lazy")
        
        if self.is_trait_high('neuroticism'):
            description.append("anxious")
        elif self.is_trait_low('neuroticism'):
            description.append("calm")
        
        if self.is_trait_high('openness'):
            description.append("creative")
        elif self.is_trait_low('openness'):
            description.append("conventional")
        
        if self.is_trait_high('risk_taking'):
            description.append("risk-taking")
        elif self.is_trait_low('risk_taking'):
            description.append("cautious")
        
        if self.is_trait_high('ambition'):
            description.append("ambitious")
        elif self.is_trait_low('ambition'):
            description.append("unambitious")
        
        if self.is_trait_high('empathy'):
            description.append("empathetic")
        elif self.is_trait_low('empathy'):
            description.append("unsympathetic")
        
        if self.is_trait_high('patience'):
            description.append("patient")
        elif self.is_trait_low('patience'):
            description.append("impatient")
        
        if self.is_trait_high('honesty'):
            description.append("honest")
        elif self.is_trait_low('honesty'):
            description.append("dishonest")
        
        if not description:
            return "average"
        
        if len(description) == 1:
            return description[0]
        
        return ", ".join(description[:-1]) + " and " + description[-1]
