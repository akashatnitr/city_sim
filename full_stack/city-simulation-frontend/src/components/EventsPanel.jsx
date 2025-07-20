import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { ScrollArea } from '@/components/ui/scroll-area.jsx'
import { AlertTriangle, Calendar, MapPin, Clock, Zap, Users, Car, Building, Heart } from 'lucide-react'

const EventsPanel = ({ events = [] }) => {
  const activeEvents = events.filter(event => event.is_active)
  const upcomingEvents = events.filter(event => !event.is_active && new Date(event.start_time) > new Date())

  const getEventIcon = (type) => {
    const icons = {
      emergency: AlertTriangle,
      weather: Zap,
      social: Users,
      traffic: Car,
      infrastructure: Building,
      health: Heart,
      holiday: Calendar
    }
    return icons[type] || AlertTriangle
  }

  const getEventColor = (type) => {
    const colors = {
      emergency: 'text-red-500',
      weather: 'text-blue-500',
      social: 'text-purple-500',
      traffic: 'text-yellow-500',
      infrastructure: 'text-gray-500',
      health: 'text-pink-500',
      holiday: 'text-green-500'
    }
    return colors[type] || 'text-gray-500'
  }

  const getSeverityVariant = (severity) => {
    const variants = {
      low: 'secondary',
      medium: 'default',
      high: 'destructive',
      critical: 'destructive'
    }
    return variants[severity] || 'secondary'
  }

  const formatTime = (timeString) => {
    try {
      return new Date(timeString).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    } catch {
      return 'Unknown'
    }
  }

  const formatDuration = (startTime, endTime) => {
    try {
      const start = new Date(startTime)
      const end = new Date(endTime)
      const diffMs = end - start
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))
      
      if (diffHours > 0) {
        return `${diffHours}h ${diffMinutes}m`
      }
      return `${diffMinutes}m`
    } catch {
      return 'Unknown'
    }
  }

  const EventItem = ({ event, isActive = true }) => {
    const EventIcon = getEventIcon(event.type)
    
    return (
      <div className="flex items-start space-x-3 p-3 rounded-lg border bg-card">
        <div className={`mt-0.5 ${getEventColor(event.type)}`}>
          <EventIcon className="h-4 w-4" />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-sm font-medium truncate">{event.name}</h4>
            <Badge variant={getSeverityVariant(event.severity)} className="text-xs">
              {event.severity}
            </Badge>
          </div>
          
          <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
            {event.description || 'No description available'}
          </p>
          
          <div className="space-y-1">
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>
                {isActive ? 'Started' : 'Starts'}: {formatTime(event.start_time)}
              </span>
            </div>
            
            {event.end_time && (
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <Clock className="h-3 w-3" />
                <span>
                  Duration: {formatDuration(event.start_time, event.end_time)}
                </span>
              </div>
            )}
            
            {event.location_id && (
              <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                <MapPin className="h-3 w-3" />
                <span>Location ID: {event.location_id}</span>
              </div>
            )}
          </div>
          
          {/* Event Effects */}
          {event.effects && Object.keys(event.effects).length > 0 && (
            <div className="mt-2 pt-2 border-t">
              <div className="text-xs text-muted-foreground mb-1">Effects:</div>
              <div className="flex flex-wrap gap-1">
                {Object.entries(event.effects).map(([key, value]) => {
                  if (value === true) {
                    return (
                      <Badge key={key} variant="outline" className="text-xs">
                        {key.replace('_', ' ')}
                      </Badge>
                    )
                  }
                  if (typeof value === 'number' && value !== 1) {
                    return (
                      <Badge key={key} variant="outline" className="text-xs">
                        {key.replace('_', ' ')}: {value}x
                      </Badge>
                    )
                  }
                  return null
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5" />
          <span>Events</span>
          {activeEvents.length > 0 && (
            <Badge variant="destructive" className="ml-2">
              {activeEvents.length}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {events.length === 0 ? (
          <div className="text-center py-6">
            <Calendar className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">No events scheduled</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Active Events */}
            {activeEvents.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-3 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                  <span>Active Events ({activeEvents.length})</span>
                </h3>
                <ScrollArea className="h-48">
                  <div className="space-y-2">
                    {activeEvents.map(event => (
                      <EventItem key={event.id} event={event} isActive={true} />
                    ))}
                  </div>
                </ScrollArea>
              </div>
            )}
            
            {/* Upcoming Events */}
            {upcomingEvents.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-3 flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Upcoming Events ({upcomingEvents.length})</span>
                </h3>
                <ScrollArea className="h-32">
                  <div className="space-y-2">
                    {upcomingEvents.slice(0, 3).map(event => (
                      <EventItem key={event.id} event={event} isActive={false} />
                    ))}
                  </div>
                </ScrollArea>
              </div>
            )}
            
            {/* Event Summary */}
            <div className="pt-2 border-t">
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <div className="text-lg font-bold text-red-600">{activeEvents.length}</div>
                  <div className="text-xs text-muted-foreground">Active</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-blue-600">{upcomingEvents.length}</div>
                  <div className="text-xs text-muted-foreground">Upcoming</div>
                </div>
              </div>
            </div>
            
            {/* Critical Events Warning */}
            {activeEvents.some(event => event.severity === 'critical') && (
              <div className="pt-2 border-t">
                <Badge variant="destructive" className="w-full justify-center animate-pulse">
                  🚨 Critical Events Active
                </Badge>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default EventsPanel

