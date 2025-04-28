#!/usr/bin/env python3
"""
AI City Simulator - Main Entry Point
"""
import sys
import os
import argparse
import pygame
import time

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.simulation import Simulation
from src.gui.display import Display
from src.utils.config import load_config


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='AI City Simulator')
    parser.add_argument('--config', type=str, default='config/default.yaml',
                        help='Path to configuration file')
    parser.add_argument('--fullscreen', action='store_true',
                        help='Start in fullscreen mode')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    return parser.parse_args()


def main():
    """Main entry point for the AI City Simulator."""
    # Parse command line arguments
    args = parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize pygame
    pygame.init()
    
    # Create simulation
    simulation = Simulation(config)
    
    # Create display
    display = Display(simulation, fullscreen=args.fullscreen, debug=args.debug)
    
    # Main loop
    running = True
    clock = pygame.time.Clock()
    
    try:
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        simulation.toggle_pause()
                    elif event.key == pygame.K_f:
                        display.toggle_fullscreen()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        simulation.increase_speed()
                    elif event.key == pygame.K_MINUS:
                        simulation.decrease_speed()
                
                # Pass events to display for handling
                display.handle_event(event)
            
            # Update simulation if not paused
            if not simulation.paused:
                simulation.update()
            
            # Render the display
            display.render()
            
            # Cap the frame rate
            clock.tick(config.get('fps', 60))
            
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
    finally:
        # Clean up
        pygame.quit()
        print("Simulation ended.")


if __name__ == "__main__":
    main()
