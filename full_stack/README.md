# City Simulation System

A comprehensive dynamic city simulation system that models real-world behaviors of diverse agents in a virtual city environment. The system features multi-agent simulation, real-time visualization, environmental dynamics, and data analytics capabilities.

## 🌟 Features

### Multi-Agent Simulation
- **Diverse Agent Roles**: Students, Software Engineers, Teachers, Restaurant Staff & Customers, Grocery Workers & Shoppers, Delivery Personnel, and other Citizens
- **Concurrent Real-time Operation**: All agents operate simultaneously with role-specific tasks and routines
- **Intelligent Behavior Patterns**: Agents follow realistic schedules and respond to environmental changes
- **Dynamic Decision Making**: AI-driven agent behaviors with route optimization and activity planning

### Advanced Environment Dynamics
- **Weather System**: Dynamic weather conditions (clear, rain, storm, snow, fog) affecting agent behavior
- **Traffic Simulation**: Realistic traffic patterns, public transportation, and commuting delays
- **Event System**: Public holidays, city festivals, emergencies (fires, accidents, power outages), and epidemics
- **Time Acceleration**: Simulate days, weeks, or months with configurable time speed (0.1x to 10x)

### Real-time Visualization
- **Interactive City Map**: Canvas-based visualization with zoom, pan, and selection capabilities
- **Agent Tracking**: Real-time agent positions, paths, and status indicators
- **Location Management**: Visual representation of buildings, roads, and transit systems
- **Event Visualization**: Dynamic event markers with severity indicators and effects

### Data Analytics & Monitoring
- **Comprehensive Statistics**: Agent distribution, location occupancy, and performance metrics
- **Real-time Dashboards**: Live monitoring of simulation state and system health
- **Activity Logging**: Detailed tracking of agent movements, activities, and interactions
- **Export Capabilities**: Data export for further analysis and reporting

## 🏗️ System Architecture

### Backend (Flask + Python)
- **Port**: 6000
- **API Framework**: Flask with RESTful endpoints
- **Real-time Communication**: WebSocket support via Socket.IO
- **Database**: SQLite with SQLAlchemy ORM
- **Simulation Engine**: Multi-threaded agent processing with pathfinding algorithms

### Frontend (React + TypeScript)
- **Framework**: React 18 with modern hooks and context
- **UI Components**: Shadcn/ui with Tailwind CSS styling
- **Real-time Updates**: Socket.IO client for live data streaming
- **Visualization**: HTML5 Canvas for high-performance map rendering
- **Responsive Design**: Mobile and desktop compatible interface

### Communication Architecture
- **REST API**: Standard HTTP endpoints for CRUD operations
- **WebSocket**: Real-time bidirectional communication for live updates
- **CORS Enabled**: Cross-origin requests supported for development and deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- pnpm package manager

### Backend Setup
```bash
cd city-simulation-backend
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

### Frontend Setup
```bash
cd city-simulation-frontend
pnpm install
pnpm run dev --host
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:6000
- **API Documentation**: http://localhost:6000/api/docs

## 📊 API Endpoints

### Simulation Control
- `POST /api/simulation/start` - Start the simulation
- `POST /api/simulation/stop` - Stop the simulation
- `GET /api/simulation/state` - Get current simulation state
- `POST /api/simulation/initialize` - Initialize city with sample data

### Agent Management
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `POST /api/agents/{id}/move` - Move agent to location

### Location & Environment
- `GET /api/simulation/locations` - Get all locations
- `GET /api/simulation/weather` - Get current weather
- `POST /api/simulation/weather` - Set weather conditions
- `GET /api/simulation/events` - List active events
- `POST /api/simulation/events` - Create new event

## 🎮 Usage Guide

### Initializing the City
1. Click "Initialize City" to create a sample city with locations, roads, and agents
2. Choose city size: Small (50-100 agents), Medium (100-200 agents), or Large (200+ agents)
3. The system will generate diverse locations (residential, offices, schools, restaurants, etc.)

### Starting the Simulation
1. Configure simulation settings in the Control Panel
2. Set time acceleration (0.1x to 10x speed)
3. Enable/disable features: Weather System, Dynamic Events, Traffic Simulation, Agent AI
4. Click "Start Simulation" to begin

### Monitoring Agents
1. Use the Agents tab to view all agents and their current status
2. Filter agents by role, status, or search by name
3. Click on any agent to view detailed information
4. Add new agents with custom roles and starting positions

### Interacting with the Map
1. **Zoom**: Use mouse wheel or zoom controls
2. **Pan**: Click and drag to move around the city
3. **Select Agents**: Click on agents to view details
4. **View Information**: Hover over elements for quick info

### Managing Events and Weather
1. Use the Control Panel to trigger events (traffic accidents, fires, festivals, power outages)
2. Set custom weather conditions with temperature and duration
3. Monitor active events in the Events panel
4. Observe how events affect agent behavior and city dynamics

## 🔧 Configuration

### Environment Variables
```bash
# Backend Configuration
FLASK_ENV=development
DATABASE_URL=sqlite:///simulation.db
CORS_ORIGINS=*

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:6000
```

### Simulation Settings
- **Time Acceleration**: 0.1x to 10x real-time speed
- **Agent AI**: Enable/disable intelligent agent behaviors
- **Weather System**: Dynamic weather effects on simulation
- **Traffic Simulation**: Realistic traffic patterns and delays
- **Event System**: Random and triggered events

## 📈 Data Communication

### WebSocket Events
The system uses WebSocket for real-time communication between frontend and backend:

#### Client → Server Events
- `start_simulation` - Start simulation with configuration
- `stop_simulation` - Stop the running simulation
- `add_agent` - Add new agent to simulation
- `move_agent` - Move agent to specific location

#### Server → Client Events
- `simulation_update` - Real-time agent positions and statistics
- `simulation_started` - Simulation start confirmation
- `simulation_stopped` - Simulation stop notification
- `agent_added` - New agent added to simulation
- `agent_removed` - Agent removed from simulation
- `event_started` - New event triggered
- `event_ended` - Event completed
- `weather_changed` - Weather conditions updated

### Data Structures

#### Agent Data
```json
{
  "id": 1,
  "name": "Software Engineer 1",
  "role": "software_engineer",
  "x": 2.5,
  "y": -1.2,
  "status": "working",
  "energy": 85.5,
  "health": 92.0,
  "current_location_id": 15,
  "target_location_id": null,
  "schedule": {...},
  "preferences": {...}
}
```

#### Location Data
```json
{
  "id": 1,
  "name": "Tech Tower #1",
  "type": "office",
  "x": 2.5,
  "y": -1.2,
  "capacity": 250,
  "current_occupancy": 45,
  "is_open": true,
  "opening_hours": {...},
  "services": ["parking", "cafeteria", "meeting_rooms"]
}
```

#### Event Data
```json
{
  "id": 1,
  "name": "Traffic Accident",
  "type": "emergency",
  "severity": "medium",
  "start_time": "2024-01-15T08:30:00Z",
  "end_time": "2024-01-15T10:30:00Z",
  "location_id": 25,
  "is_active": true,
  "effects": {
    "traffic_increase": 1.5,
    "road_blocked": true
  }
}
```

## 🧪 Testing

### Backend Testing
```bash
cd city-simulation-backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd city-simulation-frontend
pnpm test
```

### Integration Testing
1. Start both backend and frontend servers
2. Initialize a city with sample data
3. Start the simulation and verify real-time updates
4. Test agent creation and movement
5. Trigger events and verify effects
6. Test weather system functionality

## 🚀 Deployment

### Backend Deployment
The backend is configured to run on `0.0.0.0:6000` and supports CORS for cross-origin requests.

### Frontend Deployment
The frontend can be built for production and deployed to any static hosting service:
```bash
cd city-simulation-frontend
pnpm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Flask, React, and modern web technologies
- UI components powered by Shadcn/ui and Tailwind CSS
- Real-time communication via Socket.IO
- Pathfinding algorithms for realistic agent movement
- Weather and event systems for dynamic simulation

## 📞 Support

For questions, issues, or contributions, please:
1. Check the [Issues](https://github.com/your-repo/city-simulation/issues) page
2. Create a new issue with detailed description
3. Join our community discussions

---



