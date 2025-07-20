import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Users, MapPin, Activity, Clock, Zap, Heart } from 'lucide-react'

const StatisticsPanel = ({ simulationState, agents = [], locations = [], events = [] }) => {
  // Calculate statistics
  const totalAgents = agents.length
  const activeAgents = agents.filter(agent => agent.status !== 'idle').length
  const totalLocations = locations.length
  const openLocations = locations.filter(loc => loc.is_open).length
  const activeEvents = events.filter(event => event.is_active).length

  // Agent role distribution
  const roleDistribution = agents.reduce((acc, agent) => {
    acc[agent.role] = (acc[agent.role] || 0) + 1
    return acc
  }, {})

  // Location type distribution
  const locationDistribution = locations.reduce((acc, location) => {
    acc[location.type] = (acc[location.type] || 0) + 1
    return acc
  }, {})

  // Average agent stats
  const avgEnergy = agents.length > 0 
    ? agents.reduce((sum, agent) => sum + agent.energy, 0) / agents.length 
    : 0
  const avgHealth = agents.length > 0 
    ? agents.reduce((sum, agent) => sum + agent.health, 0) / agents.length 
    : 0

  // Location occupancy
  const totalCapacity = locations.reduce((sum, loc) => sum + loc.capacity, 0)
  const currentOccupancy = locations.reduce((sum, loc) => sum + loc.current_occupancy, 0)
  const occupancyRate = totalCapacity > 0 ? (currentOccupancy / totalCapacity) * 100 : 0

  return (
    <div className="space-y-4">
      {/* Main Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5" />
            <span>Simulation Status</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Status</span>
            <Badge variant={simulationState?.is_running ? "default" : "secondary"}>
              {simulationState?.is_running ? "Running" : "Stopped"}
            </Badge>
          </div>
          
          {simulationState?.current_time && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Time</span>
              <span className="text-sm font-mono">
                {new Date(simulationState.current_time).toLocaleTimeString()}
              </span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Speed</span>
            <Badge variant="outline">
              {simulationState?.time_acceleration || 1}x
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Agent Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="h-5 w-5" />
            <span>Agents</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{totalAgents}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{activeAgents}</div>
              <div className="text-xs text-muted-foreground">Active</div>
            </div>
          </div>

          {/* Average Health and Energy */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1">
                <Heart className="h-4 w-4 text-red-500" />
                <span className="text-sm">Health</span>
              </div>
              <span className="text-sm font-medium">{avgHealth.toFixed(1)}%</span>
            </div>
            <Progress value={avgHealth} className="h-2" />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-1">
                <Zap className="h-4 w-4 text-yellow-500" />
                <span className="text-sm">Energy</span>
              </div>
              <span className="text-sm font-medium">{avgEnergy.toFixed(1)}%</span>
            </div>
            <Progress value={avgEnergy} className="h-2" />
          </div>

          {/* Top Agent Roles */}
          <div className="space-y-2">
            <div className="text-sm font-medium">Top Roles</div>
            {Object.entries(roleDistribution)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 3)
              .map(([role, count]) => (
                <div key={role} className="flex items-center justify-between">
                  <span className="text-xs capitalize">
                    {role.replace('_', ' ')}
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {count}
                  </Badge>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Location Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <MapPin className="h-5 w-5" />
            <span>Locations</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{totalLocations}</div>
              <div className="text-xs text-muted-foreground">Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{openLocations}</div>
              <div className="text-xs text-muted-foreground">Open</div>
            </div>
          </div>

          {/* Occupancy Rate */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm">Occupancy</span>
              <span className="text-sm font-medium">{occupancyRate.toFixed(1)}%</span>
            </div>
            <Progress value={occupancyRate} className="h-2" />
            <div className="text-xs text-muted-foreground">
              {currentOccupancy} / {totalCapacity} capacity
            </div>
          </div>

          {/* Location Types */}
          <div className="space-y-2">
            <div className="text-sm font-medium">Types</div>
            {Object.entries(locationDistribution)
              .sort(([,a], [,b]) => b - a)
              .slice(0, 4)
              .map(([type, count]) => (
                <div key={type} className="flex items-center justify-between">
                  <span className="text-xs capitalize">{type}</span>
                  <Badge variant="outline" className="text-xs">
                    {count}
                  </Badge>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* Events Statistics */}
      {events.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Events</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{events.length}</div>
                <div className="text-xs text-muted-foreground">Total</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{activeEvents}</div>
                <div className="text-xs text-muted-foreground">Active</div>
              </div>
            </div>

            {/* Recent Events */}
            <div className="space-y-2">
              <div className="text-sm font-medium">Recent Events</div>
              {events
                .filter(event => event.is_active)
                .slice(0, 3)
                .map(event => (
                  <div key={event.id} className="flex items-center justify-between">
                    <span className="text-xs truncate">{event.name}</span>
                    <Badge 
                      variant={
                        event.severity === 'critical' ? 'destructive' :
                        event.severity === 'high' ? 'destructive' :
                        event.severity === 'medium' ? 'default' : 'secondary'
                      }
                      className="text-xs"
                    >
                      {event.severity}
                    </Badge>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Performance Statistics */}
      {simulationState?.statistics && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Performance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Ticks</span>
              <span className="text-xs font-mono">
                {simulationState.statistics.total_ticks || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Movements</span>
              <span className="text-xs font-mono">
                {simulationState.statistics.agents_moved || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">Activities</span>
              <span className="text-xs font-mono">
                {simulationState.statistics.activities_completed || 0}
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default StatisticsPanel

