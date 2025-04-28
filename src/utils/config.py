"""
Configuration module for AI City Simulator.
Handles loading and parsing configuration files.
"""
import os
import yaml


def load_config(config_path):
    """
    Load a configuration file.
    
    Args:
        config_path (str): Path to the configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    # Create default config
    default_config = {
        'city': {
            'name': 'AI City',
            'width': 2000,
            'height': 2000,
            'grid_size': 200,
            'main_road_width': 10,
            'residential_count': 100,
            'commercial_count': 50,
            'educational_count': 10,
            'transportation_count': 30,
            'recreation_count': 20,
            'service_count': 10,
        },
        'agents': {
            'initial_population': 100,
        },
        'time_scale': 60,  # 1 second real time = 1 minute sim time
        'start_hour': 8,   # Start at 8:00 AM
        'fps': 60,
        'enable_city_growth': True,
        'weather': {
            'enable_weather': True,
            'weather_change_probability': 0.001,
        },
        'crime': {
            'enable_crime': True,
            'crime_rate': 0.01,
        },
        'traffic': {
            'enable_traffic': True,
            'congestion_factor': 1.0,
        },
        'events': {
            'enable_events': True,
            'event_probability': 0.001,
        },
    }
    
    # If config path doesn't exist, create the default config
    if not os.path.exists(config_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Write the default config
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    # Load the config file
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Merge with default config to ensure all values are present
    merged_config = _merge_configs(default_config, config)
    
    return merged_config


def _merge_configs(default_config, user_config):
    """
    Merge a user config with the default config.
    
    Args:
        default_config (dict): Default configuration
        user_config (dict): User configuration
        
    Returns:
        dict: Merged configuration
    """
    if user_config is None:
        return default_config
    
    result = default_config.copy()
    
    for key, value in user_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result
