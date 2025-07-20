# City Simulation System - Technical Documentation

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Backend Implementation](#backend-implementation)
3. [Frontend Implementation](#frontend-implementation)
4. [Database Schema](#database-schema)
5. [Simulation Engine](#simulation-engine)
6. [Agent Behavior System](#agent-behavior-system)
7. [Communication Protocols](#communication-protocols)
8. [Performance Optimization](#performance-optimization)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)

## System Architecture

### Overview
The City Simulation System follows a modern client-server architecture with real-time communication capabilities. The system is designed to handle hundreds of concurrent agents while maintaining responsive user interaction and accurate simulation state.

### Architecture Components

#### Backend Services
- **Flask Application Server**: Main API server running on port 6000
- **SQLite Database**: Persistent storage for simulation data
- **WebSocket Server**: Real-time communication via Socket.IO
- **Simulation Engine**: Multi-threaded agent processing system
- **Event Manager**: Dynamic event creation and management
- **Weather System**: Environmental condition simulation

#### Frontend Application
- **React SPA**: Single-page application with modern React patterns
- **Canvas Renderer**: High-performance map visualization
- **WebSocket Client**: Real-time data synchronization
- **State Management**: React hooks and context for global state
- **UI Components**: Modular component library with Shadcn/ui

#### Communication Layer
- **REST API**: Standard HTTP endpoints for CRUD operations
- **WebSocket Protocol**: Bidirectional real-time communication
- **CORS Support**: Cross-origin resource sharing enabled
- **JSON Serialization**: Standardized data exchange format

## Backend Implementation

### Flask Application Structure
```
city-simulation-backend/
├── src/
│   ├── main.py                 # Application entry point
│   ├── models/                 # Database models
│   │   ├── agent.py           # Agent data model
│   │   ├── location.py        # Location and infrastructure
│   │   ├── event.py           # Events and simulation state
│   │   └── user.py            # Database configuration
│   ├── routes/                 # API endpoints
│   │   ├── agents.py          # Agent management routes
│   │   └── simulation.py      # Simulation control routes
│   └── simulation/             # Core simulation logic
│       ├── engine.py          # Main simulation engine
│       ├── agent_behaviors.py # Agent behavior patterns
│       ├── pathfinding.py     # Navigation algorithms
│       ├── weather_system.py  # Weather simulation
│       ├── event_manager.py   # Event handling
│       └── data_initializer.py # Sample data generation
├── requirements.txt            # Python dependencies
└── venv/                      # Virtual environment
```

### Database Models

#### Agent Model
The Agent model represents individual entities in the simulation with comprehensive state tracking:

```python
class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    x = db.Column(db.Float, default=0.0)
    y = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(50), default='idle')
    energy = db.Column(db.Float, default=100.0)
    health = db.Column(db.Float, default=100.0)
    current_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    target_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    schedule = db.Column(db.Text)  # JSON serialized schedule
    preferences = db.Column(db.Text)  # JSON serialized preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Location Model
Locations represent physical spaces in the city with capacity and operational constraints:

```python
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=100)
    current_occupancy = db.Column(db.Integer, default=0)
    is_open = db.Column(db.Boolean, default=True)
    opening_hours = db.Column(db.Text)  # JSON serialized hours
    services = db.Column(db.Text)  # JSON serialized services list
    properties = db.Column(db.Text)  # JSON serialized properties
```

### Simulation Engine

#### Core Engine Architecture
The simulation engine operates on a tick-based system with configurable time acceleration:

```python
class SimulationEngine:
    def __init__(self):
        self.is_running = False
        self.time_acceleration = 1.0
        self.current_time = datetime.utcnow()
        self.agents = []
        self.locations = []
        self.events = []
        self.weather = None
        self.statistics = {}
        
    def start_simulation(self, config=None):
        """Start the simulation with optional configuration"""
        self.is_running = True
        self.time_acceleration = config.get('time_acceleration', 1.0)
        
        # Start simulation thread
        self.simulation_thread = threading.Thread(target=self._simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
    def _simulation_loop(self):
        """Main simulation loop running in separate thread"""
        while self.is_running:
            start_time = time.time()
            
            # Update simulation time
            self._update_simulation_time()
            
            # Process all agents
            self._process_agents()
            
            # Update environment
            self._update_environment()
            
            # Process events
            self._process_events()
            
            # Update statistics
            self._update_statistics()
            
            # Emit updates via WebSocket
            self._emit_updates()
            
            # Control tick rate (60 FPS target)
            elapsed = time.time() - start_time
            sleep_time = max(0, 1/60 - elapsed)
            time.sleep(sleep_time)
```

#### Agent Processing System
Each agent is processed individually with behavior patterns specific to their role:

```python
def _process_agents(self):
    """Process all agents in the simulation"""
    for agent in self.agents:
        # Update agent state based on current activity
        self._update_agent_state(agent)
        
        # Process agent behavior based on role and schedule
        self._process_agent_behavior(agent)
        
        # Handle agent movement
        self._process_agent_movement(agent)
        
        # Update agent energy and health
        self._update_agent_vitals(agent)
        
        # Check for agent interactions
        self._process_agent_interactions(agent)
```

### Agent Behavior System

#### Behavior Pattern Implementation
Agent behaviors are implemented using a state machine pattern with role-specific logic:

```python
class AgentBehaviorSystem:
    def __init__(self):
        self.behavior_patterns = {
            'student': StudentBehavior(),
            'software_engineer': SoftwareEngineerBehavior(),
            'teacher': TeacherBehavior(),
            'restaurant_staff': RestaurantStaffBehavior(),
            # ... other role behaviors
        }
    
    def process_agent_behavior(self, agent, current_time, locations, weather):
        """Process behavior for a specific agent"""
        behavior = self.behavior_patterns.get(agent.role)
        if behavior:
            return behavior.process(agent, current_time, locations, weather)
        return self._default_behavior(agent)
```

#### Role-Specific Behaviors
Each agent role has unique behavior patterns and schedules:

**Student Behavior**:
- Morning: Travel to school
- 8:00-12:00: Attend classes
- 12:00-13:00: Lunch break
- 13:00-17:00: Study or extracurricular activities
- Evening: Return home or social activities

**Software Engineer Behavior**:
- Morning: Commute to office
- 9:00-12:00: Coding and development work
- 12:00-13:00: Lunch break
- 13:00-17:00: Meetings and collaboration
- Evening: Return home or after-work activities

### Pathfinding System

#### A* Algorithm Implementation
The pathfinding system uses the A* algorithm for efficient route calculation:

```python
class PathfindingSystem:
    def __init__(self, locations, roads):
        self.locations = {loc.id: loc for loc in locations}
        self.roads = roads
        self.graph = self._build_graph()
    
    def find_path(self, start_location_id, end_location_id):
        """Find optimal path between two locations using A* algorithm"""
        start = self.locations[start_location_id]
        end = self.locations[end_location_id]
        
        open_set = [(0, start_location_id)]
        came_from = {}
        g_score = {start_location_id: 0}
        f_score = {start_location_id: self._heuristic(start, end)}
        
        while open_set:
            current_id = heapq.heappop(open_set)[1]
            
            if current_id == end_location_id:
                return self._reconstruct_path(came_from, current_id)
            
            for neighbor_id, distance in self.graph[current_id]:
                tentative_g_score = g_score[current_id] + distance
                
                if neighbor_id not in g_score or tentative_g_score < g_score[neighbor_id]:
                    came_from[neighbor_id] = current_id
                    g_score[neighbor_id] = tentative_g_score
                    f_score[neighbor_id] = tentative_g_score + self._heuristic(
                        self.locations[neighbor_id], end
                    )
                    heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))
        
        return []  # No path found
```

## Frontend Implementation

### React Application Structure
```
city-simulation-frontend/
├── src/
│   ├── App.jsx                 # Main application component
│   ├── components/             # React components
│   │   ├── CityMap.jsx        # Canvas-based map visualization
│   │   ├── AgentPanel.jsx     # Agent management interface
│   │   ├── ControlPanel.jsx   # Simulation controls
│   │   ├── StatisticsPanel.jsx # Real-time statistics
│   │   ├── WeatherPanel.jsx   # Weather information
│   │   ├── EventsPanel.jsx    # Event monitoring
│   │   └── ui/                # Reusable UI components
│   ├── hooks/                  # Custom React hooks
│   │   └── useSimulation.js   # Simulation state management
│   ├── lib/                   # Utility functions
│   ├── assets/                # Static assets
│   ├── App.css               # Application styles
│   └── main.jsx              # Application entry point
├── public/                    # Public assets
├── package.json              # Dependencies and scripts
└── vite.config.js           # Vite configuration
```

### Canvas-Based Map Visualization

#### High-Performance Rendering
The map visualization uses HTML5 Canvas for optimal performance with hundreds of agents:

```javascript
const CityMap = ({ agents, locations, events, weather }) => {
  const canvasRef = useRef(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  
  // Render loop with requestAnimationFrame for smooth animation
  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    
    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Draw background grid
      drawGrid(ctx)
      
      // Draw locations with occupancy indicators
      locations.forEach(location => drawLocation(ctx, location))
      
      // Draw roads connecting locations
      drawRoads(ctx)
      
      // Draw active events with visual effects
      events.filter(e => e.is_active).forEach(event => drawEvent(ctx, event))
      
      // Draw agents with role-specific colors and status indicators
      agents.forEach(agent => drawAgent(ctx, agent))
      
      // Draw weather effects
      if (weather) drawWeatherEffects(ctx, weather)
    }
    
    render()
  }, [agents, locations, events, weather, zoom, pan])
  
  return (
    <canvas
      ref={canvasRef}
      width={800}
      height={600}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onWheel={handleWheel}
    />
  )
}
```

#### Interactive Features
The map supports various interactive features:

- **Zoom and Pan**: Mouse wheel zoom and click-drag panning
- **Agent Selection**: Click on agents to view detailed information
- **Hover Information**: Real-time tooltips for map elements
- **Visual Indicators**: Color-coded agents, occupancy levels, and event severity

### State Management with Custom Hooks

#### useSimulation Hook
The main simulation hook manages all application state and WebSocket communication:

```javascript
export function useSimulation() {
  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [simulationState, setSimulationState] = useState(null)
  const [agents, setAgents] = useState([])
  const [locations, setLocations] = useState([])
  const [events, setEvents] = useState([])
  const [weather, setWeather] = useState(null)
  
  // WebSocket connection and event handlers
  useEffect(() => {
    const newSocket = io('http://localhost:6000')
    
    newSocket.on('connect', () => {
      setIsConnected(true)
      loadInitialData()
    })
    
    newSocket.on('simulation_update', (data) => {
      if (data.agents) setAgents(data.agents)
      if (data.locations) setLocations(data.locations)
      if (data.weather) setWeather(data.weather)
    })
    
    // ... other event handlers
    
    setSocket(newSocket)
    return () => newSocket.close()
  }, [])
  
  // API functions
  const startSimulation = useCallback(async (config) => {
    const response = await fetch('/api/simulation/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    })
    // ... handle response
  }, [])
  
  return {
    simulationState,
    agents,
    locations,
    events,
    weather,
    isConnected,
    startSimulation,
    // ... other functions
  }
}
```

## Communication Protocols

### WebSocket Event Specification

#### Client to Server Events

**start_simulation**
```json
{
  "event": "start_simulation",
  "data": {
    "time_acceleration": 2.0,
    "settings": {
      "weather_enabled": true,
      "events_enabled": true,
      "traffic_simulation": true,
      "agent_ai_enabled": true
    }
  }
}
```

**add_agent**
```json
{
  "event": "add_agent",
  "data": {
    "name": "New Agent",
    "role": "citizen",
    "x": 0.0,
    "y": 0.0,
    "current_location_id": null
  }
}
```

#### Server to Client Events

**simulation_update**
```json
{
  "event": "simulation_update",
  "data": {
    "agents": [...],
    "locations": [...],
    "weather": {...},
    "statistics": {
      "total_ticks": 1500,
      "agents_moved": 45,
      "activities_completed": 23
    }
  }
}
```

**event_started**
```json
{
  "event": "event_started",
  "data": {
    "id": 15,
    "name": "Traffic Accident",
    "type": "emergency",
    "severity": "medium",
    "location_id": 25,
    "effects": {
      "traffic_increase": 1.5,
      "road_blocked": true
    }
  }
}
```

### REST API Specification

#### Agent Management Endpoints

**GET /api/agents**
- Description: Retrieve all agents in the simulation
- Response: Array of agent objects with full details
- Query Parameters:
  - `role`: Filter by agent role
  - `status`: Filter by agent status
  - `location_id`: Filter by current location

**POST /api/agents**
- Description: Create a new agent
- Request Body: Agent creation data
- Response: Created agent object with assigned ID

**PUT /api/agents/{id}**
- Description: Update existing agent
- Request Body: Partial agent data for updates
- Response: Updated agent object

#### Simulation Control Endpoints

**POST /api/simulation/start**
- Description: Start the simulation with configuration
- Request Body: Simulation configuration object
- Response: Simulation state and confirmation

**GET /api/simulation/state**
- Description: Get current simulation state
- Response: Complete simulation state object

**POST /api/simulation/initialize**
- Description: Initialize city with sample data
- Request Body: City size and configuration
- Response: Initialization summary and statistics

## Performance Optimization

### Backend Optimizations

#### Database Query Optimization
- **Indexed Queries**: Primary keys and foreign keys properly indexed
- **Batch Operations**: Multiple agent updates processed in batches
- **Connection Pooling**: SQLite connection pooling for concurrent access
- **Query Caching**: Frequently accessed location data cached in memory

#### Multi-threading Architecture
```python
class SimulationEngine:
    def __init__(self):
        self.agent_pool = ThreadPoolExecutor(max_workers=4)
        self.location_cache = {}
        self.update_queue = Queue()
    
    def _process_agents_parallel(self):
        """Process agents in parallel using thread pool"""
        agent_chunks = self._chunk_agents(self.agents, chunk_size=25)
        
        futures = []
        for chunk in agent_chunks:
            future = self.agent_pool.submit(self._process_agent_chunk, chunk)
            futures.append(future)
        
        # Wait for all chunks to complete
        for future in futures:
            future.result()
```

#### Memory Management
- **Object Pooling**: Reuse agent and location objects to reduce garbage collection
- **Lazy Loading**: Load detailed agent data only when requested
- **Data Compression**: Compress WebSocket messages for large data transfers

### Frontend Optimizations

#### Canvas Rendering Optimizations
```javascript
// Viewport culling - only render visible elements
const isInViewport = (x, y, zoom, pan) => {
  const screenX = x * zoom + pan.x
  const screenY = y * zoom + pan.y
  return screenX >= -50 && screenX <= canvas.width + 50 &&
         screenY >= -50 && screenY <= canvas.height + 50
}

// Level-of-detail rendering based on zoom level
const drawAgent = (ctx, agent) => {
  if (zoom < 0.5) {
    // Draw simple dots for distant view
    ctx.fillRect(x - 1, y - 1, 2, 2)
  } else if (zoom < 1.0) {
    // Draw basic circles
    ctx.arc(x, y, 3, 0, 2 * Math.PI)
  } else {
    // Draw detailed agent with status indicators
    drawDetailedAgent(ctx, agent)
  }
}
```

#### React Performance Optimizations
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: Large agent lists use virtual scrolling
- **Debounced Updates**: User input debounced to prevent excessive API calls
- **Selective Re-rendering**: Only update components when relevant data changes

## Deployment Guide

### Production Backend Deployment

#### Docker Configuration
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY run.py .

EXPOSE 6000

CMD ["python", "run.py"]
```

#### Environment Configuration
```bash
# Production environment variables
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@localhost/citydb
REDIS_URL=redis://localhost:6379
CORS_ORIGINS=https://yourdomain.com
SECRET_KEY=your-secret-key
```

### Frontend Production Build

#### Build Configuration
```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-dialog', '@radix-ui/react-select'],
          charts: ['recharts']
        }
      }
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:6000'
    }
  }
})
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        root /var/www/city-simulation/dist;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:6000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /socket.io {
        proxy_pass http://localhost:6000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Troubleshooting

### Common Issues and Solutions

#### Backend Issues

**Issue: Database Connection Errors**
```
Solution: Check database file permissions and SQLite version
- Ensure database directory is writable
- Verify SQLite3 is installed and accessible
- Check for database file corruption
```

**Issue: WebSocket Connection Failures**
```
Solution: Verify Socket.IO configuration and CORS settings
- Check CORS_ORIGINS environment variable
- Ensure port 6000 is accessible
- Verify Socket.IO client/server version compatibility
```

**Issue: High Memory Usage**
```
Solution: Optimize agent processing and implement memory management
- Reduce agent count for testing
- Implement agent pooling
- Monitor memory usage with profiling tools
```

#### Frontend Issues

**Issue: Canvas Rendering Performance**
```
Solution: Implement rendering optimizations
- Enable viewport culling
- Reduce rendering frequency for distant objects
- Use requestAnimationFrame for smooth animation
```

**Issue: WebSocket Disconnections**
```
Solution: Implement reconnection logic
- Add automatic reconnection with exponential backoff
- Handle connection state in UI
- Implement offline mode for graceful degradation
```

### Debugging Tools

#### Backend Debugging
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Profile simulation performance
import cProfile
cProfile.run('simulation_engine.run_simulation()')

# Monitor database queries
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    print(f"SQL: {statement}")
```

#### Frontend Debugging
```javascript
// Enable React DevTools profiling
if (process.env.NODE_ENV === 'development') {
  window.React = React
}

// Monitor WebSocket events
socket.onAny((event, ...args) => {
  console.log(`WebSocket Event: ${event}`, args)
})

// Performance monitoring
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach((entry) => {
    console.log(`${entry.name}: ${entry.duration}ms`)
  })
})
observer.observe({ entryTypes: ['measure'] })
```

### Performance Monitoring

#### Key Metrics to Monitor
- **Backend**: CPU usage, memory consumption, database query time, WebSocket connection count
- **Frontend**: Frame rate, memory usage, bundle size, network requests
- **Simulation**: Agent processing time, pathfinding performance, event handling latency

#### Monitoring Tools
- **Backend**: Flask-Monitor, SQLAlchemy profiling, Python memory_profiler
- **Frontend**: React DevTools Profiler, Chrome DevTools, Lighthouse
- **System**: htop, iotop, netstat for system-level monitoring

---

This technical documentation provides comprehensive coverage of the City Simulation System's implementation details, architecture decisions, and operational considerations. For additional support or advanced configuration options, refer to the individual component documentation or contact the development team.

