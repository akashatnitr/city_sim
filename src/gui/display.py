"""
Display module for AI City Simulator.
Handles the graphical user interface for the simulation.
"""
import pygame
import math
import random

class Display:
    """Handles the display of the simulation."""
    
    def __init__(self, simulation, fullscreen=False, debug=False):
        """
        Initialize the display.
        
        Args:
            simulation: The simulation instance
            fullscreen (bool): Whether to start in fullscreen mode
            debug (bool): Whether to show debug information
        """
        self.simulation = simulation
        self.debug = debug
        
        # Initialize display
        pygame.display.set_caption("AI City Simulator")
        
        # Set up the display
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
        else:
            self.width, self.height = 1280, 720
            self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Camera position and zoom
        self.camera_x = simulation.city.width // 2
        self.camera_y = simulation.city.height // 2
        self.zoom = 0.5
        self.dragging = False
        self.drag_start = None
        
        # UI elements
        self.font = pygame.font.SysFont('Arial', 14)
        self.large_font = pygame.font.SysFont('Arial', 24)
        self.selected_agent = None
        self.selected_location = None
        self.hover_agent = None
        self.hover_location = None
        
        # Filters
        self.filters = {
            'show_residential': True,
            'show_commercial': True,
            'show_educational': True,
            'show_transportation': True,
            'show_recreation': True,
            'show_service': True,
            'show_agents': True,
            'show_roads': True,
            'show_traffic': False,
            'show_crime': False,
            'show_heatmap': None,  # None, 'crime', 'traffic', 'population'
        }
        
        # Load icons
        self.icons = self._load_icons()
        
        # Colors
        self.colors = {
            'background': (200, 200, 200),
            'road': (100, 100, 100),
            'traffic_low': (100, 255, 100),
            'traffic_medium': (255, 255, 100),
            'traffic_high': (255, 100, 100),
            'residential': (200, 200, 255),
            'commercial': (255, 200, 200),
            'educational': (255, 255, 200),
            'transportation': (200, 255, 255),
            'recreation': (200, 255, 200),
            'service': (255, 200, 255),
            'text': (0, 0, 0),
            'ui_background': (240, 240, 240),
            'ui_border': (100, 100, 100),
            'ui_highlight': (100, 100, 255),
        }
    
    def _load_icons(self):
        """
        Load icons for different location types.
        
        Returns:
            dict: Dictionary of location type -> icon
        """
        # In a real implementation, we'd load actual icon images
        # For now, we'll just use colored rectangles
        icons = {}
        
        # Create a default icon (colored rectangle)
        default_icon = pygame.Surface((20, 20))
        default_icon.fill((200, 200, 200))
        
        # Define icons for different location types
        location_types = {
            'House': (200, 200, 255),
            'Apartment': (180, 180, 255),
            'Condo': (160, 160, 255),
            'Senior Living': (140, 140, 255),
            'Grocery Store': (255, 200, 200),
            'Restaurant': (255, 180, 180),
            'Coffee Shop': (255, 160, 160),
            'Bar': (255, 140, 140),
            'Gym': (255, 120, 120),
            'Shopping Mall': (255, 100, 100),
            'Elementary School': (255, 255, 200),
            'High School': (255, 255, 180),
            'College': (255, 255, 160),
            'Library': (255, 255, 140),
            'Bus Stop': (200, 255, 255),
            'Train Station': (180, 255, 255),
            'Airport': (160, 255, 255),
            'Park': (200, 255, 200),
            'Movie Theater': (180, 255, 180),
            'Sports Stadium': (160, 255, 160),
            'Museum': (140, 255, 140),
            'Police Station': (255, 200, 255),
            'Hospital': (255, 180, 255),
            'Fire Station': (255, 160, 255),
            'City Hall': (255, 140, 255),
        }
        
        # Create icons for each location type
        for loc_type, color in location_types.items():
            icon = pygame.Surface((20, 20))
            icon.fill(color)
            icons[loc_type] = icon
        
        # Use default icon for any missing types
        icons['default'] = default_icon
        
        return icons
    
    def handle_event(self, event):
        """
        Handle a pygame event.
        
        Args:
            event: The pygame event to handle
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Start dragging
                self.dragging = True
                self.drag_start = event.pos
                
                # Check if we clicked on an agent or location
                world_x, world_y = self._screen_to_world(event.pos[0], event.pos[1])
                self._handle_click(world_x, world_y)
                
            elif event.button == 4:  # Mouse wheel up
                # Zoom in
                self.zoom = min(2.0, self.zoom * 1.1)
                
            elif event.button == 5:  # Mouse wheel down
                # Zoom out
                self.zoom = max(0.1, self.zoom / 1.1)
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click
                # Stop dragging
                self.dragging = False
                
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                # Move the camera
                dx = event.pos[0] - self.drag_start[0]
                dy = event.pos[1] - self.drag_start[1]
                
                self.camera_x -= dx / self.zoom
                self.camera_y -= dy / self.zoom
                
                self.drag_start = event.pos
            
            # Check for hover
            world_x, world_y = self._screen_to_world(event.pos[0], event.pos[1])
            self._handle_hover(world_x, world_y)
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                # Toggle fullscreen
                self.toggle_fullscreen()
                
            elif event.key == pygame.K_1:
                # Toggle residential filter
                self.filters['show_residential'] = not self.filters['show_residential']
                
            elif event.key == pygame.K_2:
                # Toggle commercial filter
                self.filters['show_commercial'] = not self.filters['show_commercial']
                
            elif event.key == pygame.K_3:
                # Toggle educational filter
                self.filters['show_educational'] = not self.filters['show_educational']
                
            elif event.key == pygame.K_4:
                # Toggle transportation filter
                self.filters['show_transportation'] = not self.filters['show_transportation']
                
            elif event.key == pygame.K_5:
                # Toggle recreation filter
                self.filters['show_recreation'] = not self.filters['show_recreation']
                
            elif event.key == pygame.K_6:
                # Toggle service filter
                self.filters['show_service'] = not self.filters['show_service']
                
            elif event.key == pygame.K_a:
                # Toggle agents
                self.filters['show_agents'] = not self.filters['show_agents']
                
            elif event.key == pygame.K_r:
                # Toggle roads
                self.filters['show_roads'] = not self.filters['show_roads']
                
            elif event.key == pygame.K_t:
                # Toggle traffic
                self.filters['show_traffic'] = not self.filters['show_traffic']
                
            elif event.key == pygame.K_c:
                # Toggle crime
                self.filters['show_crime'] = not self.filters['show_crime']
                
            elif event.key == pygame.K_h:
                # Cycle heatmap
                if self.filters['show_heatmap'] is None:
                    self.filters['show_heatmap'] = 'crime'
                elif self.filters['show_heatmap'] == 'crime':
                    self.filters['show_heatmap'] = 'traffic'
                elif self.filters['show_heatmap'] == 'traffic':
                    self.filters['show_heatmap'] = 'population'
                else:
                    self.filters['show_heatmap'] = None
    
    def _handle_click(self, world_x, world_y):
        """
        Handle a click at the given world coordinates.
        
        Args:
            world_x (float): X coordinate in world space
            world_y (float): Y coordinate in world space
        """
        # Check if we clicked on an agent
        for agent in self.simulation.agent_manager.agents:
            dx = agent.x - world_x
            dy = agent.y - world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 10:
                # Clicked on this agent
                self.selected_agent = agent
                self.selected_location = None
                return
        
        # Check if we clicked on a location
        for location in self.simulation.city.get_all_locations():
            dx = location.x - world_x
            dy = location.y - world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 20:
                # Clicked on this location
                self.selected_location = location
                self.selected_agent = None
                return
        
        # Clicked on nothing
        self.selected_agent = None
        self.selected_location = None
    
    def _handle_hover(self, world_x, world_y):
        """
        Handle hovering at the given world coordinates.
        
        Args:
            world_x (float): X coordinate in world space
            world_y (float): Y coordinate in world space
        """
        # Check if we're hovering over an agent
        self.hover_agent = None
        for agent in self.simulation.agent_manager.agents:
            dx = agent.x - world_x
            dy = agent.y - world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 10:
                # Hovering over this agent
                self.hover_agent = agent
                break
        
        # Check if we're hovering over a location
        self.hover_location = None
        for location in self.simulation.city.get_all_locations():
            dx = location.x - world_x
            dy = location.y - world_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < 20:
                # Hovering over this location
                self.hover_location = location
                break
    
    def _screen_to_world(self, screen_x, screen_y):
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x (int): X coordinate on the screen
            screen_y (int): Y coordinate on the screen
            
        Returns:
            tuple: (world_x, world_y)
        """
        world_x = self.camera_x + (screen_x - self.width / 2) / self.zoom
        world_y = self.camera_y + (screen_y - self.height / 2) / self.zoom
        return world_x, world_y
    
    def _world_to_screen(self, world_x, world_y):
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x (float): X coordinate in the world
            world_y (float): Y coordinate in the world
            
        Returns:
            tuple: (screen_x, screen_y)
        """
        screen_x = (world_x - self.camera_x) * self.zoom + self.width / 2
        screen_y = (world_y - self.camera_y) * self.zoom + self.height / 2
        return int(screen_x), int(screen_y)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.screen.get_flags() & pygame.FULLSCREEN:
            # Switch to windowed mode
            self.screen = pygame.display.set_mode((1280, 720))
            self.width, self.height = 1280, 720
        else:
            # Switch to fullscreen mode
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
    
    def render(self):
        """Render the display."""
        # Clear the screen
        self.screen.fill(self.colors['background'])
        
        # Render the city
        self._render_city()
        
        # Render the agents
        if self.filters['show_agents']:
            self._render_agents()
        
        # Render UI
        self._render_ui()
        
        # Update the display
        pygame.display.flip()
    
    def _render_city(self):
        """Render the city."""
        # Render roads
        if self.filters['show_roads']:
            self._render_roads()
        
        # Render locations
        self._render_locations()
        
        # Render heatmap
        if self.filters['show_heatmap']:
            self._render_heatmap()
    
    def _render_roads(self):
        """Render the roads."""
        # Get the road network
        road_network = self.simulation.city.road_network
        
        # Render each edge
        for edge in road_network.graph.edges():
            # Get the edge coordinates
            x1, y1 = edge[0]
            x2, y2 = edge[1]
            
            # Convert to screen coordinates
            screen_x1, screen_y1 = self._world_to_screen(x1, y1)
            screen_x2, screen_y2 = self._world_to_screen(x2, y2)
            
            # Check if the edge is visible on screen
            if (0 <= screen_x1 <= self.width or 0 <= screen_x2 <= self.width) and \
               (0 <= screen_y1 <= self.height or 0 <= screen_y2 <= self.height):
                
                # Determine the color based on traffic
                if self.filters['show_traffic']:
                    traffic = road_network.get_traffic_level(edge)
                    if traffic < 0.3:
                        color = self.colors['traffic_low']
                    elif traffic < 0.7:
                        color = self.colors['traffic_medium']
                    else:
                        color = self.colors['traffic_high']
                else:
                    color = self.colors['road']
                
                # Draw the road
                pygame.draw.line(self.screen, color, (screen_x1, screen_y1), (screen_x2, screen_y2), 2)
    
    def _render_locations(self):
        """Render the locations."""
        # Get all locations
        all_locations = self.simulation.city.get_all_locations()
        
        # Filter locations based on filters
        filtered_locations = []
        for location in all_locations:
            if location.category == 'residential' and self.filters['show_residential'] or \
               location.category == 'commercial' and self.filters['show_commercial'] or \
               location.category == 'educational' and self.filters['show_educational'] or \
               location.category == 'transportation' and self.filters['show_transportation'] or \
               location.category == 'recreation' and self.filters['show_recreation'] or \
               location.category == 'service' and self.filters['show_service']:
                filtered_locations.append(location)
        
        # Render each location
        for location in filtered_locations:
            # Convert to screen coordinates
            screen_x, screen_y = self._world_to_screen(location.x, location.y)
            
            # Check if the location is visible on screen
            if 0 <= screen_x <= self.width and 0 <= screen_y <= self.height:
                # Get the icon for this location type
                icon = self.icons.get(location.location_type, self.icons['default'])
                
                # Scale the icon based on zoom
                icon_size = int(20 * self.zoom)
                if icon_size < 5:
                    icon_size = 5
                
                scaled_icon = pygame.transform.scale(icon, (icon_size, icon_size))
                
                # Draw the icon
                self.screen.blit(scaled_icon, (screen_x - icon_size // 2, screen_y - icon_size // 2))
                
                # If this is the selected or hovered location, draw additional info
                if location == self.selected_location or location == self.hover_location:
                    # Draw a highlight
                    pygame.draw.circle(self.screen, self.colors['ui_highlight'], (screen_x, screen_y), icon_size + 2, 2)
                    
                    # Draw the name
                    text = self.font.render(location.name, True, self.colors['text'])
                    self.screen.blit(text, (screen_x - text.get_width() // 2, screen_y + icon_size + 2))
    
    def _render_agents(self):
        """Render the agents."""
        # Get all agents
        all_agents = self.simulation.agent_manager.agents
        
        # Render each agent
        for agent in all_agents:
            # Convert to screen coordinates
            screen_x, screen_y = self._world_to_screen(agent.x, agent.y)
            
            # Check if the agent is visible on screen
            if 0 <= screen_x <= self.width and 0 <= screen_y <= self.height:
                # Get the color for this agent type
                color = agent.get_color()
                
                # Draw the agent
                agent_size = int(5 * self.zoom)
                if agent_size < 2:
                    agent_size = 2
                
                pygame.draw.circle(self.screen, color, (screen_x, screen_y), agent_size)
                
                # If this is the selected or hovered agent, draw additional info
                if agent == self.selected_agent or agent == self.hover_agent:
                    # Draw a highlight
                    pygame.draw.circle(self.screen, self.colors['ui_highlight'], (screen_x, screen_y), agent_size + 2, 2)
                    
                    # Draw the name
                    text = self.font.render(agent.name, True, self.colors['text'])
                    self.screen.blit(text, (screen_x - text.get_width() // 2, screen_y + agent_size + 2))
    
    def _render_heatmap(self):
        """Render a heatmap overlay."""
        # Different heatmaps
        if self.filters['show_heatmap'] == 'crime':
            self._render_crime_heatmap()
        elif self.filters['show_heatmap'] == 'traffic':
            self._render_traffic_heatmap()
        elif self.filters['show_heatmap'] == 'population':
            self._render_population_heatmap()
    
    def _render_crime_heatmap(self):
        """Render a crime heatmap."""
        # In a real implementation, we'd use actual crime data
        # For now, just render random hotspots
        for _ in range(10):
            x = random.randint(0, self.simulation.city.width)
            y = random.randint(0, self.simulation.city.height)
            intensity = random.random()
            
            screen_x, screen_y = self._world_to_screen(x, y)
            
            # Draw a red circle with alpha based on intensity
            surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 0, 0, int(100 * intensity)), (50, 50), 50)
            self.screen.blit(surface, (screen_x - 50, screen_y - 50))
    
    def _render_traffic_heatmap(self):
        """Render a traffic heatmap."""
        # In a real implementation, we'd use actual traffic data
        # For now, just render random hotspots
        for _ in range(10):
            x = random.randint(0, self.simulation.city.width)
            y = random.randint(0, self.simulation.city.height)
            intensity = random.random()
            
            screen_x, screen_y = self._world_to_screen(x, y)
            
            # Draw a yellow circle with alpha based on intensity
            surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            pygame.draw.circle(surface, (255, 255, 0, int(100 * intensity)), (50, 50), 50)
            self.screen.blit(surface, (screen_x - 50, screen_y - 50))
    
    def _render_population_heatmap(self):
        """Render a population heatmap."""
        # Get all agents
        all_agents = self.simulation.agent_manager.agents
        
        # Create a grid to count agents
        grid_size = 100
        grid_width = self.simulation.city.width // grid_size + 1
        grid_height = self.simulation.city.height // grid_size + 1
        grid = [[0 for _ in range(grid_height)] for _ in range(grid_width)]
        
        # Count agents in each grid cell
        for agent in all_agents:
            grid_x = int(agent.x) // grid_size
            grid_y = int(agent.y) // grid_size
            
            if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
                grid[grid_x][grid_y] += 1
        
        # Find the maximum count
        max_count = 1
        for x in range(grid_width):
            for y in range(grid_height):
                max_count = max(max_count, grid[x][y])
        
        # Render each grid cell
        for x in range(grid_width):
            for y in range(grid_height):
                count = grid[x][y]
                if count > 0:
                    # Calculate intensity
                    intensity = count / max_count
                    
                    # Convert to screen coordinates
                    screen_x, screen_y = self._world_to_screen(x * grid_size + grid_size // 2, y * grid_size + grid_size // 2)
                    
                    # Draw a blue circle with alpha based on intensity
                    surface = pygame.Surface((grid_size * 2, grid_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(surface, (0, 0, 255, int(100 * intensity)), (grid_size, grid_size), grid_size)
                    self.screen.blit(surface, (screen_x - grid_size, screen_y - grid_size))
    
    def _render_ui(self):
        """Render the user interface."""
        # Render time
        time_str = self.simulation.get_time_str()
        text = self.large_font.render(time_str, True, self.colors['text'])
        self.screen.blit(text, (10, 10))
        
        # Render speed
        speed_str = f"Speed: {self.simulation.speed}x"
        text = self.font.render(speed_str, True, self.colors['text'])
        self.screen.blit(text, (10, 40))
        
        # Render agent count
        agent_count = self.simulation.agent_manager.get_agent_count()
        text = self.font.render(f"Agents: {agent_count}", True, self.colors['text'])
        self.screen.blit(text, (10, 60))
        
        # Render weather
        weather = self.simulation.weather_system.get_current_weather()
        text = self.font.render(f"Weather: {weather}", True, self.colors['text'])
        self.screen.blit(text, (10, 80))
        
        # Render filter status
        y = 120
        text = self.font.render("Filters:", True, self.colors['text'])
        self.screen.blit(text, (10, y))
        y += 20
        
        for filter_name, enabled in self.filters.items():
            if filter_name == 'show_heatmap':
                text = self.font.render(f"{filter_name}: {enabled}", True, self.colors['text'])
            else:
                text = self.font.render(f"{filter_name}: {'On' if enabled else 'Off'}", True, self.colors['text'])
            self.screen.blit(text, (20, y))
            y += 20
        
        # Render selected agent or location info
        if self.selected_agent:
            self._render_agent_info(self.selected_agent)
        elif self.selected_location:
            self._render_location_info(self.selected_location)
    
    def _render_agent_info(self, agent):
        """
        Render information about the selected agent.
        
        Args:
            agent: The agent to render information for
        """
        # Create a panel in the bottom right
        panel_width = 300
        panel_height = 300
        panel_x = self.width - panel_width - 10
        panel_y = self.height - panel_height - 10
        
        # Draw the panel background
        pygame.draw.rect(self.screen, self.colors['ui_background'], (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.colors['ui_border'], (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw the agent name
        text = self.large_font.render(agent.name, True, self.colors['text'])
        self.screen.blit(text, (panel_x + 10, panel_y + 10))
        
        # Draw agent details
        y = panel_y + 50
        details = [
            f"Age: {agent.age}",
            f"Gender: {agent.gender}",
            f"Type: {agent.agent_type}",
            f"Personality: {agent.personality.get_description()}",
            f"Location: {agent.current_location.name if agent.current_location else 'Unknown'}",
            f"Activity: {agent.current_activity or 'None'}",
            f"State: {agent.state}",
            f"Transportation: {agent.transportation_mode}"
        ]
        
        for detail in details:
            text = self.font.render(detail, True, self.colors['text'])
            self.screen.blit(text, (panel_x + 10, y))
            y += 20
        
        # Draw needs
        y += 10
        text = self.font.render("Needs:", True, self.colors['text'])
        self.screen.blit(text, (panel_x + 10, y))
        y += 20
        
        for name, need in agent.needs.items():
            # Draw need bar
            bar_width = 150
            bar_height = 10
            bar_x = panel_x + 100
            
            # Background
            pygame.draw.rect(self.screen, self.colors['ui_border'], (bar_x, y, bar_width, bar_height))
            
            # Fill based on value
            fill_width = int(bar_width * need.value / 100)
            pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, y, fill_width, bar_height))
            
            # Label
            text = self.font.render(f"{name}: {need.value:.0f}", True, self.colors['text'])
            self.screen.blit(text, (panel_x + 10, y - 2))
            
            y += 15
    
    def _render_location_info(self, location):
        """
        Render information about the selected location.
        
        Args:
            location: The location to render information for
        """
        # Create a panel in the bottom right
        panel_width = 300
        panel_height = 200
        panel_x = self.width - panel_width - 10
        panel_y = self.height - panel_height - 10
        
        # Draw the panel background
        pygame.draw.rect(self.screen, self.colors['ui_background'], (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, self.colors['ui_border'], (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Draw the location name
        text = self.large_font.render(location.name, True, self.colors['text'])
        self.screen.blit(text, (panel_x + 10, panel_y + 10))
        
        # Draw location details
        y = panel_y + 50
        details = [
            f"Type: {location.location_type}",
            f"Category: {location.category}",
            f"Capacity: {location.capacity}",
            f"Current Occupancy: {location.get_agent_count()}"
        ]
        
        for detail in details:
            text = self.font.render(detail, True, self.colors['text'])
            self.screen.blit(text, (panel_x + 10, y))
            y += 20
        
        # Draw agents at this location
        y += 10
        text = self.font.render(f"Agents ({len(location.agents)}):", True, self.colors['text'])
        self.screen.blit(text, (panel_x + 10, y))
        y += 20
        
        # Show up to 5 agents
        for i, agent in enumerate(location.agents[:5]):
            text = self.font.render(f"{agent.name} ({agent.agent_type})", True, self.colors['text'])
            self.screen.blit(text, (panel_x + 20, y))
            y += 20
        
        # If there are more agents, show a count
        if len(location.agents) > 5:
            text = self.font.render(f"...and {len(location.agents) - 5} more", True, self.colors['text'])
            self.screen.blit(text, (panel_x + 20, y))
