"""
Configuration management for the options analyzer tool.
"""

import os
import yaml
from typing import Dict, Any


def get_config_path() -> str:
    """
    Get the path to the configuration file.
    
    Returns:
        Path to the configuration file
    """
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to the config directory
    config_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'config')
    
    # Check if the config directory exists, if not create it
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    return os.path.join(config_dir, 'settings.yaml')


def load_config() -> Dict[str, Any]:
    """
    Load the configuration from the YAML file.
    
    Returns:
        Dictionary containing configuration values
    """
    config_path = get_config_path()
    
    # If the config file doesn't exist, create it with default values
    if not os.path.exists(config_path):
        default_config = {
            'min_premium_percent': 0.5,
            'max_days_to_expiry': 45,
            'show_ai_analysis': True,
            'default_strategy': 'cash_secured_put',
            'default_ticker': 'SPY',
        }
        save_config(default_config)
        return default_config
    
    # Load the config file
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config if config else {}
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return {}


def save_config(config: Dict[str, Any]) -> bool:
    """
    Save the configuration to the YAML file.
    
    Args:
        config: Dictionary containing configuration values
        
    Returns:
        True if successful, False otherwise
    """
    config_path = get_config_path()
    
    try:
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Error saving config file: {str(e)}")
        return False


def update_config(key: str, value: Any) -> bool:
    """
    Update a specific configuration value.
    
    Args:
        key: Configuration key to update
        value: New value for the key
        
    Returns:
        True if successful, False otherwise
    """
    # Load the current config
    config = load_config()
    
    # Update the value
    config[key] = value
    
    # Save the updated config
    return save_config(config)