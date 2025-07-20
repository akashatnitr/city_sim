import { useState, useEffect, useRef } from 'react'
import { Card } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Button } from '@/components/ui/button.jsx'
import { ZoomIn, ZoomOut, RotateCcw, MapPin, Users, AlertTriangle } from 'lucide-react'

const CityMap = ({ 
  agents = [], 
  locations = [], 
  events = [], 
  weather = null,
  onAgentSelect,
  selectedAgent 
}) => {
  const canvasRef = useRef(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [hoveredItem, setHoveredItem] = useState(null)

  // Map dimensions and scale
  const MAP_WIDTH = 800
  const MAP_HEIGHT = 600
  const WORLD_SIZE = 20 // 20km x 20km world

  // Convert world coordinates to canvas coordinates
  const worldToCanvas = (worldX, worldY) => {
    const canvasX = ((worldX + WORLD_SIZE/2) / WORLD_SIZE) * MAP_WIDTH * zoom + pan.x
    const canvasY = ((worldY + WORLD_SIZE/2) / WORLD_SIZE) * MAP_HEIGHT * zoom + pan.y
    return { x: canvasX, y: canvasY }
  }

  // Convert canvas coordinates to world coordinates
  const canvasToWorld = (canvasX, canvasY) => {
    const worldX = ((canvasX - pan.x) / (MAP_WIDTH * zoom)) * WORLD_SIZE - WORLD_SIZE/2
    const worldY = ((canvasY - pan.y) / (MAP_HEIGHT * zoom)) * WORLD_SIZE - WORLD_SIZE/2
    return { x: worldX, y: worldY }
  }

  // Draw the map
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw background grid
    drawGrid(ctx)

    // Draw locations
    locations.forEach(location => drawLocation(ctx, location))

    // Draw roads (simplified - just lines between nearby locations)
    drawRoads(ctx)

    // Draw events
    events.filter(event => event.is_active).forEach(event => drawEvent(ctx, event))

    // Draw agents
    agents.forEach(agent => drawAgent(ctx, agent))

    // Draw weather effects
    if (weather) {
      drawWeatherEffects(ctx, weather)
    }

    // Draw selection highlight
    if (selectedAgent) {
      drawSelectionHighlight(ctx, selectedAgent)
    }

  }, [agents, locations, events, weather, selectedAgent, zoom, pan])

  const drawGrid = (ctx) => {
    ctx.strokeStyle = '#e2e8f0'
    ctx.lineWidth = 1
    
    const gridSize = 50 * zoom
    const offsetX = pan.x % gridSize
    const offsetY = pan.y % gridSize

    // Vertical lines
    for (let x = offsetX; x < MAP_WIDTH; x += gridSize) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, MAP_HEIGHT)
      ctx.stroke()
    }

    // Horizontal lines
    for (let y = offsetY; y < MAP_HEIGHT; y += gridSize) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(MAP_WIDTH, y)
      ctx.stroke()
    }
  }

  const drawLocation = (ctx, location) => {
    const pos = worldToCanvas(location.x, location.y)
    
    // Skip if outside visible area
    if (pos.x < -50 || pos.x > MAP_WIDTH + 50 || pos.y < -50 || pos.y > MAP_HEIGHT + 50) {
      return
    }

    const size = Math.max(8, Math.min(20, location.capacity / 10)) * zoom

    // Location type colors
    const colors = {
      residential: '#10b981',
      office: '#3b82f6',
      school: '#f59e0b',
      restaurant: '#ef4444',
      shop: '#8b5cf6',
      hospital: '#ec4899',
      park: '#22c55e',
      transit: '#6366f1'
    }

    ctx.fillStyle = colors[location.type] || '#64748b'
    ctx.strokeStyle = location.is_open ? '#ffffff' : '#ef4444'
    ctx.lineWidth = 2

    // Draw location as circle
    ctx.beginPath()
    ctx.arc(pos.x, pos.y, size, 0, 2 * Math.PI)
    ctx.fill()
    ctx.stroke()

    // Draw occupancy indicator
    if (location.current_occupancy > 0) {
      const occupancyRatio = location.current_occupancy / location.capacity
      const indicatorSize = size * 0.6
      
      ctx.fillStyle = occupancyRatio > 0.8 ? '#ef4444' : occupancyRatio > 0.5 ? '#f59e0b' : '#10b981'
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, indicatorSize, 0, 2 * Math.PI * occupancyRatio)
      ctx.fill()
    }

    // Draw label if zoomed in enough
    if (zoom > 0.8) {
      ctx.fillStyle = '#1f2937'
      ctx.font = `${Math.max(10, 12 * zoom)}px sans-serif`
      ctx.textAlign = 'center'
      ctx.fillText(location.name, pos.x, pos.y + size + 15)
    }
  }

  const drawRoads = (ctx) => {
    ctx.strokeStyle = '#94a3b8'
    ctx.lineWidth = Math.max(1, 2 * zoom)

    // Simple road network - connect nearby locations
    locations.forEach(location1 => {
      locations.forEach(location2 => {
        if (location1.id >= location2.id) return

        const distance = Math.sqrt(
          Math.pow(location1.x - location2.x, 2) + 
          Math.pow(location1.y - location2.y, 2)
        )

        if (distance < 5) { // Connect locations within 5km
          const pos1 = worldToCanvas(location1.x, location1.y)
          const pos2 = worldToCanvas(location2.x, location2.y)

          ctx.beginPath()
          ctx.moveTo(pos1.x, pos1.y)
          ctx.lineTo(pos2.x, pos2.y)
          ctx.stroke()
        }
      })
    })
  }

  const drawAgent = (ctx, agent) => {
    const pos = worldToCanvas(agent.x, agent.y)
    
    // Skip if outside visible area
    if (pos.x < -20 || pos.x > MAP_WIDTH + 20 || pos.y < -20 || pos.y > MAP_HEIGHT + 20) {
      return
    }

    const size = Math.max(3, 6 * zoom)

    // Agent role colors
    const colors = {
      student: '#3b82f6',
      software_engineer: '#8b5cf6',
      teacher: '#f59e0b',
      restaurant_staff: '#ef4444',
      restaurant_customer: '#ec4899',
      grocery_worker: '#10b981',
      grocery_shopper: '#22c55e',
      delivery_personnel: '#f97316',
      citizen: '#64748b',
      police_officer: '#1e40af',
      firefighter: '#dc2626',
      doctor: '#059669',
      nurse: '#0891b2',
      bus_driver: '#7c3aed',
      taxi_driver: '#ca8a04'
    }

    // Agent status affects appearance
    const isSelected = selectedAgent && selectedAgent.id === agent.id
    const isMoving = agent.status === 'moving'

    ctx.fillStyle = colors[agent.role] || '#64748b'
    ctx.strokeStyle = isSelected ? '#fbbf24' : isMoving ? '#ffffff' : 'transparent'
    ctx.lineWidth = isSelected ? 3 : 1

    // Draw agent as circle
    ctx.beginPath()
    ctx.arc(pos.x, pos.y, size, 0, 2 * Math.PI)
    ctx.fill()
    if (ctx.strokeStyle !== 'transparent') {
      ctx.stroke()
    }

    // Draw energy/health indicator
    const healthRatio = agent.health / 100
    const energyRatio = agent.energy / 100
    
    if (healthRatio < 1 || energyRatio < 0.5) {
      ctx.fillStyle = healthRatio < 0.3 ? '#ef4444' : energyRatio < 0.3 ? '#f59e0b' : '#10b981'
      ctx.beginPath()
      ctx.arc(pos.x + size, pos.y - size, 2, 0, 2 * Math.PI)
      ctx.fill()
    }

    // Draw movement trail for moving agents
    if (isMoving && agent.target_location_id) {
      const targetLocation = locations.find(loc => loc.id === agent.target_location_id)
      if (targetLocation) {
        const targetPos = worldToCanvas(targetLocation.x, targetLocation.y)
        
        ctx.strokeStyle = colors[agent.role] || '#64748b'
        ctx.lineWidth = 1
        ctx.setLineDash([5, 5])
        
        ctx.beginPath()
        ctx.moveTo(pos.x, pos.y)
        ctx.lineTo(targetPos.x, targetPos.y)
        ctx.stroke()
        
        ctx.setLineDash([])
      }
    }

    // Draw label if selected or zoomed in
    if (isSelected || zoom > 1.5) {
      ctx.fillStyle = '#1f2937'
      ctx.font = `${Math.max(8, 10 * zoom)}px sans-serif`
      ctx.textAlign = 'center'
      ctx.fillText(agent.name, pos.x, pos.y - size - 5)
    }
  }

  const drawEvent = (ctx, event) => {
    if (!event.location_id) return // Skip city-wide events for now

    const location = locations.find(loc => loc.id === event.location_id)
    if (!location) return

    const pos = worldToCanvas(location.x, location.y)
    const size = 15 * zoom

    // Event type colors
    const colors = {
      emergency: '#ef4444',
      weather: '#3b82f6',
      social: '#8b5cf6',
      traffic: '#f59e0b',
      infrastructure: '#64748b',
      health: '#ec4899'
    }

    ctx.fillStyle = colors[event.type] || '#ef4444'
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 2

    // Draw event as triangle
    ctx.beginPath()
    ctx.moveTo(pos.x, pos.y - size)
    ctx.lineTo(pos.x - size * 0.8, pos.y + size * 0.5)
    ctx.lineTo(pos.x + size * 0.8, pos.y + size * 0.5)
    ctx.closePath()
    ctx.fill()
    ctx.stroke()

    // Draw pulsing effect for high severity events
    if (event.severity === 'high' || event.severity === 'critical') {
      const pulseSize = size * (1 + 0.3 * Math.sin(Date.now() / 200))
      ctx.strokeStyle = colors[event.type] || '#ef4444'
      ctx.lineWidth = 1
      ctx.globalAlpha = 0.3
      
      ctx.beginPath()
      ctx.arc(pos.x, pos.y, pulseSize, 0, 2 * Math.PI)
      ctx.stroke()
      
      ctx.globalAlpha = 1
    }
  }

  const drawWeatherEffects = (ctx, weather) => {
    if (weather.condition === 'rain' || weather.condition === 'storm') {
      // Draw rain effect
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 1
      ctx.globalAlpha = 0.3

      for (let i = 0; i < 100; i++) {
        const x = Math.random() * MAP_WIDTH
        const y = Math.random() * MAP_HEIGHT
        
        ctx.beginPath()
        ctx.moveTo(x, y)
        ctx.lineTo(x + 2, y + 10)
        ctx.stroke()
      }
      
      ctx.globalAlpha = 1
    }

    if (weather.condition === 'fog') {
      // Draw fog effect
      ctx.fillStyle = '#94a3b8'
      ctx.globalAlpha = 0.2
      ctx.fillRect(0, 0, MAP_WIDTH, MAP_HEIGHT)
      ctx.globalAlpha = 1
    }
  }

  const drawSelectionHighlight = (ctx, agent) => {
    const pos = worldToCanvas(agent.x, agent.y)
    const size = 20 * zoom

    ctx.strokeStyle = '#fbbf24'
    ctx.lineWidth = 3
    ctx.setLineDash([5, 5])

    ctx.beginPath()
    ctx.arc(pos.x, pos.y, size, 0, 2 * Math.PI)
    ctx.stroke()

    ctx.setLineDash([])
  }

  // Mouse event handlers
  const handleMouseDown = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    setIsDragging(true)
    setDragStart({ x: x - pan.x, y: y - pan.y })

    // Check for agent selection
    const worldPos = canvasToWorld(x, y)
    const clickedAgent = agents.find(agent => {
      const distance = Math.sqrt(
        Math.pow(agent.x - worldPos.x, 2) + 
        Math.pow(agent.y - worldPos.y, 2)
      )
      return distance < 0.5 // 500m selection radius
    })

    if (clickedAgent && onAgentSelect) {
      onAgentSelect(clickedAgent)
    }
  }

  const handleMouseMove = (e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    if (isDragging) {
      setPan({
        x: x - dragStart.x,
        y: y - dragStart.y
      })
    } else {
      // Check for hover effects
      const worldPos = canvasToWorld(x, y)
      const hoveredAgent = agents.find(agent => {
        const distance = Math.sqrt(
          Math.pow(agent.x - worldPos.x, 2) + 
          Math.pow(agent.y - worldPos.y, 2)
        )
        return distance < 0.5
      })

      const hoveredLocation = locations.find(location => {
        const distance = Math.sqrt(
          Math.pow(location.x - worldPos.x, 2) + 
          Math.pow(location.y - worldPos.y, 2)
        )
        return distance < 1
      })

      setHoveredItem(hoveredAgent || hoveredLocation || null)
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleWheel = (e) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    setZoom(prev => Math.max(0.1, Math.min(3, prev * delta)))
  }

  const resetView = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  return (
    <div className="relative">
      {/* Map Controls */}
      <div className="absolute top-4 right-4 z-10 flex flex-col space-y-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setZoom(prev => Math.min(3, prev * 1.2))}
        >
          <ZoomIn className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setZoom(prev => Math.max(0.1, prev * 0.8))}
        >
          <ZoomOut className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={resetView}
        >
          <RotateCcw className="h-4 w-4" />
        </Button>
      </div>

      {/* Map Legend */}
      <div className="absolute top-4 left-4 z-10">
        <Card className="p-3 bg-white/90 backdrop-blur-sm">
          <div className="text-sm font-medium mb-2">Legend</div>
          <div className="space-y-1 text-xs">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-blue-500"></div>
              <span>Offices</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-green-500"></div>
              <span>Residential</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 rounded-full bg-purple-500"></div>
              <span>Agents</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500" style={{ clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }}></div>
              <span>Events</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Hover Info */}
      {hoveredItem && (
        <div className="absolute bottom-4 left-4 z-10">
          <Card className="p-3 bg-white/90 backdrop-blur-sm">
            <div className="text-sm font-medium">
              {hoveredItem.name}
            </div>
            <div className="text-xs text-muted-foreground">
              {hoveredItem.role ? `Role: ${hoveredItem.role}` : `Type: ${hoveredItem.type}`}
            </div>
            {hoveredItem.status && (
              <Badge variant="outline" className="mt-1">
                {hoveredItem.status}
              </Badge>
            )}
          </Card>
        </div>
      )}

      {/* Map Canvas */}
      <canvas
        ref={canvasRef}
        width={MAP_WIDTH}
        height={MAP_HEIGHT}
        className="border rounded-lg cursor-move bg-slate-50"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
      />

      {/* Map Info */}
      <div className="absolute bottom-4 right-4 z-10">
        <Card className="p-2 bg-white/90 backdrop-blur-sm">
          <div className="text-xs text-muted-foreground">
            Zoom: {zoom.toFixed(1)}x | Agents: {agents.length} | Locations: {locations.length}
          </div>
        </Card>
      </div>
    </div>
  )
}

export default CityMap

