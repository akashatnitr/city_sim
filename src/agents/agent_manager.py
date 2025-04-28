"""
Agent manager module for AI City Simulator.
Manages all agents in the simulation.
"""
import random
from src.agents.person import Person
from src.agents.personality import Personality
from src.agents.goal import Goal


class AgentManager:
    """Manages all agents in the simulation."""
    
    def __init__(self, simulation, config):
        """
        Initialize the agent manager.
        
        Args:
            simulation: The simulation instance
            config (dict): Configuration dictionary for agents
        """
        self.simulation = simulation
        self.config = config
        self.agents = []
        
        # Agent types and their proportions
        self.agent_types = {
            'resident': 0.7,
            'worker': 0.1,
            'student': 0.1,
            'police': 0.03,
            'criminal': 0.02,
            'visitor': 0.05,
        }
        
        # Generate initial agents
        self._generate_initial_agents()
    
    def _generate_initial_agents(self):
        """Generate the initial set of agents."""
        # Get the total number of agents to generate
        total_agents = self.config.get('initial_population', 100)
        
        # Generate agents based on their proportions
        for agent_type, proportion in self.agent_types.items():
            count = int(total_agents * proportion)
            
            for _ in range(count):
                self._create_agent(agent_type)
    
    def _create_agent(self, agent_type):
        """
        Create a new agent of the specified type.
        
        Args:
            agent_type (str): Type of agent to create
            
        Returns:
            Person: The created agent
        """
        # Generate a name for the agent
        first_names = {
            'male': ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles',
                     'Daniel', 'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth'],
            'female': ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen',
                       'Lisa', 'Nancy', 'Betty', 'Sandra', 'Margaret', 'Ashley', 'Kimberly', 'Emily', 'Donna', 'Michelle']
        }
        last_names = ['Smith', 'Johnson', 'Williams', 'Jones', 'Brown', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor',
                      'Anderson', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin', 'Thompson', 'Garcia', 'Martinez', 'Robinson']
        
        gender = random.choice(['male', 'female'])
        first_name = random.choice(first_names[gender])
        last_name = random.choice(last_names)
        
        # Generate a random age appropriate for the agent type
        if agent_type == 'student':
            age = random.randint(6, 22)
        elif agent_type in ['worker', 'resident', 'police', 'criminal']:
            age = random.randint(18, 65)
        elif agent_type == 'visitor':
            age = random.randint(18, 80)
        else:
            age = random.randint(18, 80)
        
        # Create a personality for the agent
        personality = Personality.generate_random()
        
        # Set initial location
        city = self.simulation.city
        
        # Choose an appropriate initial location based on agent type
        if agent_type == 'resident':
            # Start at a residential location
            locations = city.get_locations_by_category('residential')
            if locations:
                initial_location = random.choice(locations)
            else:
                # Fallback to a random location
                initial_location = random.choice(city.get_all_locations())
        
        elif agent_type == 'worker':
            # Start at a commercial or service location
            locations = (city.get_locations_by_category('commercial') + 
                        city.get_locations_by_category('service'))
            if locations:
                initial_location = random.choice(locations)
            else:
                # Fallback to a random location
                initial_location = random.choice(city.get_all_locations())
        
        elif agent_type == 'student':
            # Start at an educational location
            locations = city.get_locations_by_category('educational')
            if locations:
                initial_location = random.choice(locations)
            else:
                # Fallback to a random location
                initial_location = random.choice(city.get_all_locations())
        
        elif agent_type == 'police':
            # Start at a police station
            locations = city.get_locations_by_type('Police Station')
            if locations:
                initial_location = random.choice(locations)
            else:
                # Fallback to a service location
                locations = city.get_locations_by_category('service')
                if locations:
                    initial_location = random.choice(locations)
                else:
                    # Fallback to a random location
                    initial_location = random.choice(city.get_all_locations())
        
        elif agent_type == 'criminal':
            # Start at a random location
            initial_location = random.choice(city.get_all_locations())
        
        elif agent_type == 'visitor':
            # Start at a transportation location
            locations = city.get_locations_by_category('transportation')
            if locations:
                initial_location = random.choice(locations)
            else:
                # Fallback to a random location
                initial_location = random.choice(city.get_all_locations())
        
        else:
            # Default to a random location
            initial_location = random.choice(city.get_all_locations())
        
        # Create the agent
        agent = Person(
            name=f"{first_name} {last_name}",
            age=age,
            gender=gender,
            agent_type=agent_type,
            personality=personality,
            initial_location=initial_location,
            simulation=self.simulation
        )
        
        # Add the agent to the list
        self.agents.append(agent)
        
        # Add the agent to its initial location
        initial_location.add_agent(agent)
        
        return agent
    
    def update(self):
        """Update all agents."""
        for agent in self.agents:
            agent.update()
    
    def get_agent_count(self):
        """Get the total number of agents."""
        return len(self.agents)
    
    def get_agents_by_type(self, agent_type):
        """
        Get all agents of a specific type.
        
        Args:
            agent_type (str): Type of agents to get
            
        Returns:
            list: List of agents of the specified type
        """
        return [agent for agent in self.agents if agent.agent_type == agent_type]
    
    def get_agents_at_location(self, location):
        """
        Get all agents at a specific location.
        
        Args:
            location: Location to check
            
        Returns:
            list: List of agents at the specified location
        """
        return [agent for agent in self.agents if agent.current_location == location]
    
    def get_agents_in_area(self, x, y, radius):
        """
        Get all agents within a circular area.
        
        Args:
            x (float): X coordinate of the center
            y (float): Y coordinate of the center
            radius (float): Radius of the area
            
        Returns:
            list: List of agents within the area
        """
        return [agent for agent in self.agents 
                if ((agent.x - x) ** 2 + (agent.y - y) ** 2) ** 0.5 <= radius]
