import { useState, useEffect, useCallback } from 'react'
import { io } from 'socket.io-client'

const API_BASE_URL = 'http://localhost:8000'

export function useSimulation() {
  const [socket, setSocket] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const [simulationState, setSimulationState] = useState(null)
  const [agents, setAgents] = useState([])
  const [locations, setLocations] = useState([])
  const [events, setEvents] = useState([])
  const [weather, setWeather] = useState(null)

  // Initialize WebSocket connection
  useEffect(() => {
    const newSocket = io(API_BASE_URL, {
      transports: ['websocket', 'polling']
    })

    newSocket.on('connect', () => {
      console.log('Connected to simulation server')
      setIsConnected(true)
      // Load initial data
      loadInitialData()
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from simulation server')
      setIsConnected(false)
    })

    // Listen for simulation updates
    newSocket.on('simulation_update', (data) => {
      console.log('Simulation update received:', data)
      if (data.agents) setAgents(data.agents)
      if (data.locations) setLocations(data.locations)
      if (data.weather) setWeather(data.weather)
      if (data.statistics) {
        setSimulationState(prev => ({
          ...prev,
          statistics: data.statistics
        }))
      }
    })

    newSocket.on('simulation_started', (data) => {
      console.log('Simulation started')
      setSimulationState(prev => ({
        ...prev,
        is_running: true,
        ...data
      }))
    })

    newSocket.on('simulation_stopped', () => {
      console.log('Simulation stopped')
      setSimulationState(prev => ({
        ...prev,
        is_running: false
      }))
    })

    newSocket.on('agent_added', (agentData) => {
      console.log('Agent added:', agentData)
      setAgents(prev => [...prev, agentData])
    })

    newSocket.on('agent_removed', (data) => {
      console.log('Agent removed:', data)
      setAgents(prev => prev.filter(agent => agent.id !== data.id))
    })

    newSocket.on('event_started', (eventData) => {
      console.log('Event started:', eventData)
      setEvents(prev => [...prev, eventData])
    })

    newSocket.on('event_ended', (eventData) => {
      console.log('Event ended:', eventData)
      setEvents(prev => prev.map(event => 
        event.id === eventData.id 
          ? { ...event, is_active: false }
          : event
      ))
    })

    newSocket.on('weather_changed', (weatherData) => {
      console.log('Weather changed:', weatherData)
      setWeather(weatherData)
    })

    setSocket(newSocket)

    return () => {
      newSocket.close()
    }
  }, [])

  // Load initial data from REST API
  const loadInitialData = useCallback(async () => {
    try {
      // Load simulation state
      const stateResponse = await fetch(`${API_BASE_URL}/api/simulation/state`)
      if (stateResponse.ok) {
        const stateData = await stateResponse.json()
        setSimulationState(stateData)
      }

      // Load agents
      const agentsResponse = await fetch(`${API_BASE_URL}/api/agents`)
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json()
        setAgents(agentsData)
      }

      // Load locations
      const locationsResponse = await fetch(`${API_BASE_URL}/api/simulation/locations`)
      if (locationsResponse.ok) {
        const locationsData = await locationsResponse.json()
        setLocations(locationsData)
      }

      // Load events
      const eventsResponse = await fetch(`${API_BASE_URL}/api/simulation/events`)
      if (eventsResponse.ok) {
        const eventsData = await eventsResponse.json()
        setEvents(eventsData)
      }

      // Load weather
      const weatherResponse = await fetch(`${API_BASE_URL}/api/simulation/weather`)
      if (weatherResponse.ok) {
        const weatherData = await weatherResponse.json()
        setWeather(weatherData)
      }
    } catch (error) {
      console.error('Error loading initial data:', error)
    }
  }, [])

  // Start simulation
  const startSimulation = useCallback(async (config = {}) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulation/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
      })

      if (response.ok) {
        const data = await response.json()
        setSimulationState(data.state)
        
        // Also emit via WebSocket
        if (socket) {
          socket.emit('start_simulation', config)
        }
      }
    } catch (error) {
      console.error('Error starting simulation:', error)
    }
  }, [socket])

  // Stop simulation
  const stopSimulation = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulation/stop`, {
        method: 'POST'
      })

      if (response.ok) {
        setSimulationState(prev => ({
          ...prev,
          is_running: false
        }))
        
        // Also emit via WebSocket
        if (socket) {
          socket.emit('stop_simulation')
        }
      }
    } catch (error) {
      console.error('Error stopping simulation:', error)
    }
  }, [socket])

  // Add agent
  const addAgent = useCallback(async (agentData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(agentData)
      })

      if (response.ok) {
        const newAgent = await response.json()
        setAgents(prev => [...prev, newAgent])
        
        // Also emit via WebSocket
        if (socket) {
          socket.emit('add_agent', newAgent)
        }
        
        return newAgent
      }
    } catch (error) {
      console.error('Error adding agent:', error)
    }
  }, [socket])

  // Initialize city
  const initializeCity = useCallback(async (citySize = 'medium') => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulation/initialize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ city_size: citySize })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('City initialized:', data)
        
        // Reload all data
        await loadInitialData()
        
        return data
      }
    } catch (error) {
      console.error('Error initializing city:', error)
    }
  }, [loadInitialData])

  // Update agent
  const updateAgent = useCallback(async (agentId, updates) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agents/${agentId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      })

      if (response.ok) {
        const updatedAgent = await response.json()
        setAgents(prev => prev.map(agent => 
          agent.id === agentId ? updatedAgent : agent
        ))
        return updatedAgent
      }
    } catch (error) {
      console.error('Error updating agent:', error)
    }
  }, [])

  // Move agent
  const moveAgent = useCallback(async (agentId, x, y, locationId = null) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/agents/${agentId}/move`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ x, y, location_id: locationId })
      })

      if (response.ok) {
        const data = await response.json()
        setAgents(prev => prev.map(agent => 
          agent.id === agentId ? data.agent : agent
        ))
        return data
      }
    } catch (error) {
      console.error('Error moving agent:', error)
    }
  }, [])

  // Create event
  const createEvent = useCallback(async (eventData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/simulation/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(eventData)
      })

      if (response.ok) {
        const newEvent = await response.json()
        setEvents(prev => [...prev, newEvent])
        return newEvent
      }
    } catch (error) {
      console.error('Error creating event:', error)
    }
  }, [])

  return {
    // State
    simulationState,
    agents,
    locations,
    events,
    weather,
    isConnected,
    
    // Actions
    startSimulation,
    stopSimulation,
    addAgent,
    updateAgent,
    moveAgent,
    initializeCity,
    createEvent,
    loadInitialData
  }
}

