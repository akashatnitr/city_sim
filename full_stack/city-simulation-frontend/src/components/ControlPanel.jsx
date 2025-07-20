import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Slider } from '@/components/ui/slider.jsx'
import { Switch } from '@/components/ui/switch.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { 
  Settings, 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Zap, 
  Database, 
  Clock,
  Thermometer,
  Cloud,
  AlertTriangle
} from 'lucide-react'

const ControlPanel = ({ 
  simulationState, 
  onStartSimulation, 
  onStopSimulation, 
  onInitializeCity 
}) => {
  const [timeAcceleration, setTimeAcceleration] = useState(1)
  const [citySize, setCitySize] = useState('medium')
  const [weatherEnabled, setWeatherEnabled] = useState(true)
  const [eventsEnabled, setEventsEnabled] = useState(true)
  const [trafficSimulation, setTrafficSimulation] = useState(true)
  const [agentAI, setAgentAI] = useState(true)
  const [customWeather, setCustomWeather] = useState({
    condition: 'clear',
    temperature: 20,
    duration: 2
  })

  const handleStartSimulation = () => {
    const config = {
      time_acceleration: timeAcceleration,
      settings: {
        weather_enabled: weatherEnabled,
        events_enabled: eventsEnabled,
        traffic_simulation: trafficSimulation,
        agent_ai_enabled: agentAI
      }
    }
    onStartSimulation(config)
  }

  const handleInitializeCity = () => {
    onInitializeCity(citySize)
  }

  const handleSetWeather = async () => {
    try {
      const response = await fetch('http://localhost:6000/api/simulation/weather', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          condition: customWeather.condition,
          temperature: customWeather.temperature,
          start_time: new Date().toISOString(),
          end_time: new Date(Date.now() + customWeather.duration * 60 * 60 * 1000).toISOString()
        })
      })
      
      if (response.ok) {
        console.log('Weather set successfully')
      }
    } catch (error) {
      console.error('Error setting weather:', error)
    }
  }

  const handleCreateEvent = async (eventType) => {
    const eventTemplates = {
      traffic_accident: {
        name: 'Traffic Accident',
        type: 'emergency',
        severity: 'medium',
        description: 'Traffic accident causing road delays'
      },
      fire_emergency: {
        name: 'Building Fire',
        type: 'emergency',
        severity: 'high',
        description: 'Emergency fire requiring evacuation'
      },
      festival: {
        name: 'City Festival',
        type: 'social',
        severity: 'low',
        description: 'Local festival with increased foot traffic'
      },
      power_outage: {
        name: 'Power Outage',
        type: 'infrastructure',
        severity: 'medium',
        description: 'Power outage affecting city services'
      }
    }

    const template = eventTemplates[eventType]
    if (!template) return

    try {
      const response = await fetch('http://localhost:6000/api/simulation/events', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...template,
          start_time: new Date().toISOString(),
          end_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString() // 2 hours
        })
      })
      
      if (response.ok) {
        console.log('Event created successfully')
      }
    } catch (error) {
      console.error('Error creating event:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Simulation Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Settings className="h-5 w-5" />
            <span>Simulation Controls</span>
          </CardTitle>
          <CardDescription>
            Start, stop, and configure the city simulation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Main Controls */}
          <div className="flex items-center space-x-4">
            <Button
              variant={simulationState?.is_running ? "destructive" : "default"}
              onClick={simulationState?.is_running ? onStopSimulation : handleStartSimulation}
              className="flex items-center space-x-2"
            >
              {simulationState?.is_running ? (
                <>
                  <Pause className="h-4 w-4" />
                  <span>Stop Simulation</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  <span>Start Simulation</span>
                </>
              )}
            </Button>
            
            <Button variant="outline" onClick={handleInitializeCity}>
              <Database className="h-4 w-4 mr-2" />
              Initialize City
            </Button>
          </div>

          {/* Status */}
          <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
            <span className="text-sm font-medium">Status</span>
            <Badge variant={simulationState?.is_running ? "default" : "secondary"}>
              {simulationState?.is_running ? "Running" : "Stopped"}
            </Badge>
          </div>

          <Separator />

          {/* Time Acceleration */}
          <div className="space-y-3">
            <Label className="flex items-center space-x-2">
              <Clock className="h-4 w-4" />
              <span>Time Acceleration: {timeAcceleration}x</span>
            </Label>
            <Slider
              value={[timeAcceleration]}
              onValueChange={(value) => setTimeAcceleration(value[0])}
              min={0.1}
              max={10}
              step={0.1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>0.1x (Slow)</span>
              <span>1x (Real-time)</span>
              <span>10x (Fast)</span>
            </div>
          </div>

          <Separator />

          {/* City Size */}
          <div className="space-y-3">
            <Label>City Size</Label>
            <Select value={citySize} onValueChange={setCitySize}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="small">Small (50-100 agents)</SelectItem>
                <SelectItem value="medium">Medium (100-200 agents)</SelectItem>
                <SelectItem value="large">Large (200+ agents)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          {/* Simulation Features */}
          <div className="space-y-4">
            <Label className="text-base font-medium">Simulation Features</Label>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Cloud className="h-4 w-4" />
                  <Label htmlFor="weather-enabled">Weather System</Label>
                </div>
                <Switch
                  id="weather-enabled"
                  checked={weatherEnabled}
                  onCheckedChange={setWeatherEnabled}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="h-4 w-4" />
                  <Label htmlFor="events-enabled">Dynamic Events</Label>
                </div>
                <Switch
                  id="events-enabled"
                  checked={eventsEnabled}
                  onCheckedChange={setEventsEnabled}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Zap className="h-4 w-4" />
                  <Label htmlFor="traffic-simulation">Traffic Simulation</Label>
                </div>
                <Switch
                  id="traffic-simulation"
                  checked={trafficSimulation}
                  onCheckedChange={setTrafficSimulation}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Settings className="h-4 w-4" />
                  <Label htmlFor="agent-ai">Agent AI Behaviors</Label>
                </div>
                <Switch
                  id="agent-ai"
                  checked={agentAI}
                  onCheckedChange={setAgentAI}
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Weather Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Cloud className="h-5 w-5" />
            <span>Weather Controls</span>
          </CardTitle>
          <CardDescription>
            Manually set weather conditions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Condition</Label>
              <Select
                value={customWeather.condition}
                onValueChange={(value) => setCustomWeather(prev => ({ ...prev, condition: value }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="clear">Clear</SelectItem>
                  <SelectItem value="cloudy">Cloudy</SelectItem>
                  <SelectItem value="rain">Rain</SelectItem>
                  <SelectItem value="storm">Storm</SelectItem>
                  <SelectItem value="snow">Snow</SelectItem>
                  <SelectItem value="fog">Fog</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Duration (hours)</Label>
              <Input
                type="number"
                value={customWeather.duration}
                onChange={(e) => setCustomWeather(prev => ({ 
                  ...prev, 
                  duration: parseInt(e.target.value) || 2 
                }))}
                min="1"
                max="24"
              />
            </div>
          </div>

          <div>
            <Label className="flex items-center space-x-2">
              <Thermometer className="h-4 w-4" />
              <span>Temperature: {customWeather.temperature}°C</span>
            </Label>
            <Slider
              value={[customWeather.temperature]}
              onValueChange={(value) => setCustomWeather(prev => ({ 
                ...prev, 
                temperature: value[0] 
              }))}
              min={-20}
              max={45}
              step={1}
              className="w-full mt-2"
            />
          </div>

          <Button onClick={handleSetWeather} className="w-full">
            Apply Weather
          </Button>
        </CardContent>
      </Card>

      {/* Event Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="h-5 w-5" />
            <span>Event Controls</span>
          </CardTitle>
          <CardDescription>
            Trigger events in the simulation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button
            variant="outline"
            onClick={() => handleCreateEvent('traffic_accident')}
            className="w-full justify-start"
          >
            🚗 Traffic Accident
          </Button>
          
          <Button
            variant="outline"
            onClick={() => handleCreateEvent('fire_emergency')}
            className="w-full justify-start"
          >
            🔥 Fire Emergency
          </Button>
          
          <Button
            variant="outline"
            onClick={() => handleCreateEvent('festival')}
            className="w-full justify-start"
          >
            🎉 City Festival
          </Button>
          
          <Button
            variant="outline"
            onClick={() => handleCreateEvent('power_outage')}
            className="w-full justify-start"
          >
            ⚡ Power Outage
          </Button>
        </CardContent>
      </Card>

      {/* System Information */}
      {simulationState && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">System Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Current Time</span>
              <span className="font-mono">
                {simulationState.current_time ? 
                  new Date(simulationState.current_time).toLocaleString() : 
                  'Not started'
                }
              </span>
            </div>
            
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Time Acceleration</span>
              <span className="font-mono">{simulationState.time_acceleration}x</span>
            </div>
            
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Total Agents</span>
              <span className="font-mono">{simulationState.total_agents}</span>
            </div>
            
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Active Agents</span>
              <span className="font-mono">{simulationState.active_agents}</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ControlPanel

