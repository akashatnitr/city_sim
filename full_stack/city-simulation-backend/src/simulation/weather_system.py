import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class WeatherSystem:
    """Manages weather conditions and their effects on the simulation"""
    
    def __init__(self, simulation_engine):
        self.simulation_engine = simulation_engine
        self.current_weather = {
            'condition': 'clear',
            'temperature': 20.0,
            'humidity': 50.0,
            'wind_speed': 5.0,
            'visibility': 10.0,
            'precipitation': 0.0
        }
        self.weather_history = []
        self.last_weather_change = datetime.utcnow()
        self.weather_change_interval = timedelta(hours=2)  # Change weather every 2 hours
        
        # Weather transition probabilities
        self.weather_transitions = {
            'clear': {'clear': 0.7, 'cloudy': 0.2, 'rain': 0.1},
            'cloudy': {'clear': 0.3, 'cloudy': 0.4, 'rain': 0.25, 'storm': 0.05},
            'rain': {'rain': 0.5, 'cloudy': 0.3, 'clear': 0.15, 'storm': 0.05},
            'storm': {'storm': 0.3, 'rain': 0.4, 'cloudy': 0.3},
            'snow': {'snow': 0.6, 'cloudy': 0.3, 'clear': 0.1},
            'fog': {'fog': 0.4, 'cloudy': 0.4, 'clear': 0.2}
        }
        
        # Seasonal temperature ranges (Celsius)
        self.seasonal_temps = {
            'spring': (10, 25),
            'summer': (20, 35),
            'autumn': (5, 20),
            'winter': (-5, 15)
        }
    
    def update(self, current_time: datetime):
        """Update weather conditions"""
        # Check if it's time for weather change
        if current_time - self.last_weather_change >= self.weather_change_interval:
            self._generate_new_weather(current_time)
            self.last_weather_change = current_time
        
        # Apply gradual changes
        self._apply_gradual_changes(current_time)
        
        # Store weather history
        self._record_weather_history(current_time)
    
    def _generate_new_weather(self, current_time: datetime):
        """Generate new weather conditions"""
        current_condition = self.current_weather['condition']
        
        # Get season for temperature adjustment
        season = self._get_season(current_time)
        
        # Choose next weather condition based on transitions
        transitions = self.weather_transitions.get(current_condition, {'clear': 1.0})
        next_condition = self._weighted_choice(transitions)
        
        # Update weather parameters
        self.current_weather['condition'] = next_condition
        self.current_weather['temperature'] = self._generate_temperature(season, next_condition)
        self.current_weather['humidity'] = self._generate_humidity(next_condition)
        self.current_weather['wind_speed'] = self._generate_wind_speed(next_condition)
        self.current_weather['visibility'] = self._generate_visibility(next_condition)
        self.current_weather['precipitation'] = self._generate_precipitation(next_condition)
        
        # Emit weather change event
        self.simulation_engine.emit_update('weather_changed', self.current_weather)
    
    def _apply_gradual_changes(self, current_time: datetime):
        """Apply gradual changes to weather parameters"""
        # Small random fluctuations
        temp_change = random.uniform(-0.5, 0.5)
        self.current_weather['temperature'] += temp_change
        
        humidity_change = random.uniform(-2.0, 2.0)
        self.current_weather['humidity'] = max(0, min(100, 
            self.current_weather['humidity'] + humidity_change))
        
        wind_change = random.uniform(-1.0, 1.0)
        self.current_weather['wind_speed'] = max(0, 
            self.current_weather['wind_speed'] + wind_change)
    
    def _get_season(self, current_time: datetime) -> str:
        """Determine current season based on date"""
        month = current_time.month
        
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _weighted_choice(self, choices: Dict[str, float]) -> str:
        """Make a weighted random choice"""
        total = sum(choices.values())
        r = random.uniform(0, total)
        
        cumulative = 0
        for choice, weight in choices.items():
            cumulative += weight
            if r <= cumulative:
                return choice
        
        return list(choices.keys())[0]  # Fallback
    
    def _generate_temperature(self, season: str, condition: str) -> float:
        """Generate temperature based on season and condition"""
        min_temp, max_temp = self.seasonal_temps[season]
        base_temp = random.uniform(min_temp, max_temp)
        
        # Adjust based on weather condition
        adjustments = {
            'clear': 0,
            'cloudy': -2,
            'rain': -5,
            'storm': -8,
            'snow': -10,
            'fog': -3
        }
        
        return base_temp + adjustments.get(condition, 0)
    
    def _generate_humidity(self, condition: str) -> float:
        """Generate humidity based on weather condition"""
        base_humidity = {
            'clear': random.uniform(30, 60),
            'cloudy': random.uniform(50, 80),
            'rain': random.uniform(80, 95),
            'storm': random.uniform(85, 100),
            'snow': random.uniform(70, 90),
            'fog': random.uniform(90, 100)
        }
        
        return base_humidity.get(condition, 50.0)
    
    def _generate_wind_speed(self, condition: str) -> float:
        """Generate wind speed based on weather condition"""
        wind_ranges = {
            'clear': (0, 10),
            'cloudy': (5, 15),
            'rain': (10, 25),
            'storm': (25, 50),
            'snow': (5, 20),
            'fog': (0, 5)
        }
        
        min_wind, max_wind = wind_ranges.get(condition, (0, 10))
        return random.uniform(min_wind, max_wind)
    
    def _generate_visibility(self, condition: str) -> float:
        """Generate visibility based on weather condition"""
        visibility_ranges = {
            'clear': (8, 15),
            'cloudy': (5, 12),
            'rain': (2, 8),
            'storm': (0.5, 3),
            'snow': (1, 5),
            'fog': (0.1, 2)
        }
        
        min_vis, max_vis = visibility_ranges.get(condition, (5, 15))
        return random.uniform(min_vis, max_vis)
    
    def _generate_precipitation(self, condition: str) -> float:
        """Generate precipitation amount (mm/h)"""
        precipitation_ranges = {
            'clear': (0, 0),
            'cloudy': (0, 0.1),
            'rain': (1, 10),
            'storm': (10, 50),
            'snow': (0.5, 5),
            'fog': (0, 0.2)
        }
        
        min_precip, max_precip = precipitation_ranges.get(condition, (0, 0))
        return random.uniform(min_precip, max_precip)
    
    def _record_weather_history(self, current_time: datetime):
        """Record weather data for history"""
        weather_record = {
            'timestamp': current_time.isoformat(),
            **self.current_weather
        }
        
        self.weather_history.append(weather_record)
        
        # Keep only last 24 hours of history
        cutoff_time = current_time - timedelta(hours=24)
        self.weather_history = [
            record for record in self.weather_history
            if datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
    
    def get_current_weather(self) -> Dict:
        """Get current weather conditions"""
        return self.current_weather.copy()
    
    def get_weather_history(self, hours: int = 24) -> List[Dict]:
        """Get weather history for specified hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            record for record in self.weather_history
            if datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')) > cutoff_time
        ]
    
    def get_movement_modifier(self) -> float:
        """Get movement speed modifier based on weather"""
        condition = self.current_weather['condition']
        visibility = self.current_weather['visibility']
        wind_speed = self.current_weather['wind_speed']
        precipitation = self.current_weather['precipitation']
        
        # Base modifier by condition
        condition_modifiers = {
            'clear': 1.0,
            'cloudy': 0.95,
            'rain': 0.8,
            'storm': 0.6,
            'snow': 0.7,
            'fog': 0.75
        }
        
        modifier = condition_modifiers.get(condition, 1.0)
        
        # Apply visibility effects
        if visibility < 2:
            modifier *= 0.7
        elif visibility < 5:
            modifier *= 0.85
        
        # Apply wind effects
        if wind_speed > 30:
            modifier *= 0.8
        elif wind_speed > 20:
            modifier *= 0.9
        
        # Apply precipitation effects
        if precipitation > 20:
            modifier *= 0.7
        elif precipitation > 5:
            modifier *= 0.85
        
        return max(0.3, modifier)  # Minimum 30% speed
    
    def get_energy_modifier(self) -> float:
        """Get energy consumption modifier based on weather"""
        temperature = self.current_weather['temperature']
        condition = self.current_weather['condition']
        
        # Temperature effects on energy
        if temperature < 0 or temperature > 35:
            temp_modifier = 1.3  # Extreme temperatures increase energy consumption
        elif temperature < 10 or temperature > 30:
            temp_modifier = 1.1
        else:
            temp_modifier = 1.0
        
        # Weather condition effects
        condition_modifiers = {
            'clear': 1.0,
            'cloudy': 1.0,
            'rain': 1.2,
            'storm': 1.5,
            'snow': 1.4,
            'fog': 1.1
        }
        
        condition_modifier = condition_modifiers.get(condition, 1.0)
        
        return temp_modifier * condition_modifier
    
    def is_severe_weather(self) -> bool:
        """Check if current weather is severe"""
        condition = self.current_weather['condition']
        wind_speed = self.current_weather['wind_speed']
        precipitation = self.current_weather['precipitation']
        visibility = self.current_weather['visibility']
        
        return (condition in ['storm', 'snow'] or 
                wind_speed > 40 or 
                precipitation > 25 or 
                visibility < 1)
    
    def set_weather(self, condition: str, temperature: float = None, 
                   duration_hours: int = 2):
        """Manually set weather conditions"""
        self.current_weather['condition'] = condition
        
        if temperature is not None:
            self.current_weather['temperature'] = temperature
        
        # Update other parameters based on condition
        self.current_weather['humidity'] = self._generate_humidity(condition)
        self.current_weather['wind_speed'] = self._generate_wind_speed(condition)
        self.current_weather['visibility'] = self._generate_visibility(condition)
        self.current_weather['precipitation'] = self._generate_precipitation(condition)
        
        # Set next change time
        self.last_weather_change = datetime.utcnow()
        self.weather_change_interval = timedelta(hours=duration_hours)
        
        # Emit weather change event
        self.simulation_engine.emit_update('weather_changed', self.current_weather)

