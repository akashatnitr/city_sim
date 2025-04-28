"""
Weather system module for AI City Simulator.
Manages weather conditions in the simulation.
"""
import random


class WeatherSystem:
    """Manages weather conditions in the simulation."""
    
    def __init__(self, simulation, config):
        """
        Initialize the weather system.
        
        Args:
            simulation: The simulation instance
            config (dict): Configuration dictionary for weather
        """
        self.simulation = simulation
        self.config = config
        self.enable_weather = config.get('enable_weather', True)
        self.weather_change_probability = config.get('weather_change_probability', 0.001)
        
        # Weather conditions
        self.weather_conditions = ['clear', 'cloudy', 'rain', 'heavy_rain', 'thunderstorm', 'snow', 'fog']
        self.weather_weights = [0.5, 0.2, 0.1, 0.05, 0.05, 0.05, 0.05]
        
        # Current weather
        self.current_weather = 'clear'
        self.weather_intensity = 0.5  # 0.0 to 1.0
        self.weather_duration = 0
        self.weather_transition = 0.0  # 0.0 to 1.0
        
        # Effects of weather on simulation
        self.weather_effects = {
            'clear': {
                'traffic_modifier': 1.0,
                'crime_modifier': 1.0,
                'movement_speed_modifier': 1.0,
            },
            'cloudy': {
                'traffic_modifier': 1.0,
                'crime_modifier': 1.0,
                'movement_speed_modifier': 1.0,
            },
            'rain': {
                'traffic_modifier': 1.2,  # More traffic in rain
                'crime_modifier': 0.8,    # Less crime in rain
                'movement_speed_modifier': 0.8,  # Slower movement in rain
            },
            'heavy_rain': {
                'traffic_modifier': 1.5,  # Much more traffic in heavy rain
                'crime_modifier': 0.6,    # Much less crime in heavy rain
                'movement_speed_modifier': 0.6,  # Much slower movement in heavy rain
            },
            'thunderstorm': {
                'traffic_modifier': 2.0,  # Severe traffic in thunderstorm
                'crime_modifier': 0.5,    # Much less crime in thunderstorm
                'movement_speed_modifier': 0.5,  # Much slower movement in thunderstorm
            },
            'snow': {
                'traffic_modifier': 2.0,  # Severe traffic in snow
                'crime_modifier': 0.7,    # Less crime in snow
                'movement_speed_modifier': 0.5,  # Much slower movement in snow
            },
            'fog': {
                'traffic_modifier': 1.5,  # More traffic in fog
                'crime_modifier': 1.2,    # More crime in fog
                'movement_speed_modifier': 0.7,  # Slower movement in fog
            },
        }
    
    def update(self):
        """Update the weather conditions."""
        if not self.enable_weather:
            return
        
        # Update weather duration
        self.weather_duration += 1
        
        # Check if we should change the weather
        if random.random() < self.weather_change_probability * self.simulation.speed:
            self._change_weather()
    
    def _change_weather(self):
        """Change the weather to a new condition."""
        # Choose a new weather condition
        new_weather = random.choices(self.weather_conditions, weights=self.weather_weights)[0]
        
        # Don't change to the same weather
        if new_weather == self.current_weather:
            return
        
        # Set the new weather
        self.current_weather = new_weather
        self.weather_intensity = random.uniform(0.3, 1.0)
        self.weather_duration = 0
        
        print(f"Weather changed to {self.current_weather} (intensity: {self.weather_intensity:.2f})")
    
    def get_current_weather(self):
        """
        Get the current weather condition.
        
        Returns:
            str: Current weather condition
        """
        return self.current_weather
    
    def get_weather_intensity(self):
        """
        Get the current weather intensity.
        
        Returns:
            float: Current weather intensity (0.0 to 1.0)
        """
        return self.weather_intensity
    
    def get_weather_effect(self, effect_name):
        """
        Get the effect of the current weather on a specific aspect.
        
        Args:
            effect_name (str): Name of the effect to get
            
        Returns:
            float: Effect modifier
        """
        weather_effects = self.weather_effects.get(self.current_weather, {})
        base_modifier = weather_effects.get(effect_name, 1.0)
        
        # Scale by intensity
        return 1.0 + (base_modifier - 1.0) * self.weather_intensity
