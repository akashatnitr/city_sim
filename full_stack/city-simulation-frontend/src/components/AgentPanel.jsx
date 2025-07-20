import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Users, Plus, MapPin, Activity, Heart, Zap, Clock } from 'lucide-react'

const AgentPanel = ({ agents = [], locations = [], onAgentSelect, selectedAgent, onAddAgent }) => {
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [newAgent, setNewAgent] = useState({
    name: '',
    role: '',
    x: 0,
    y: 0,
    current_location_id: null
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [filterRole, setFilterRole] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')

  const agentRoles = [
    'student', 'software_engineer', 'teacher', 'restaurant_staff',
    'restaurant_customer', 'grocery_worker', 'grocery_shopper',
    'delivery_personnel', 'citizen', 'police_officer', 'firefighter',
    'doctor', 'nurse', 'bus_driver', 'taxi_driver'
  ]

  // Filter agents
  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         agent.role.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesRole = filterRole === 'all' || agent.role === filterRole
    const matchesStatus = filterStatus === 'all' || agent.status === filterStatus
    
    return matchesSearch && matchesRole && matchesStatus
  })

  const handleAddAgent = async () => {
    if (!newAgent.name || !newAgent.role) return

    const agentData = {
      ...newAgent,
      energy: 100,
      health: 100,
      status: 'idle'
    }

    try {
      await onAddAgent(agentData)
      setNewAgent({ name: '', role: '', x: 0, y: 0, current_location_id: null })
      setShowAddDialog(false)
    } catch (error) {
      console.error('Error adding agent:', error)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      idle: 'secondary',
      moving: 'default',
      working: 'default',
      eating: 'default',
      sleeping: 'secondary',
      studying: 'default',
      shopping: 'default',
      waiting: 'secondary'
    }
    return colors[status] || 'secondary'
  }

  const getRoleColor = (role) => {
    const colors = {
      student: 'bg-blue-500',
      software_engineer: 'bg-purple-500',
      teacher: 'bg-yellow-500',
      restaurant_staff: 'bg-red-500',
      restaurant_customer: 'bg-pink-500',
      grocery_worker: 'bg-green-500',
      grocery_shopper: 'bg-emerald-500',
      delivery_personnel: 'bg-orange-500',
      citizen: 'bg-gray-500',
      police_officer: 'bg-blue-700',
      firefighter: 'bg-red-700',
      doctor: 'bg-green-700',
      nurse: 'bg-cyan-500',
      bus_driver: 'bg-violet-500',
      taxi_driver: 'bg-amber-500'
    }
    return colors[role] || 'bg-gray-500'
  }

  return (
    <div className="space-y-6">
      {/* Agent Controls */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <span>Agents ({filteredAgents.length})</span>
            </CardTitle>
            
            <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
              <DialogTrigger asChild>
                <Button size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Agent
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add New Agent</DialogTitle>
                  <DialogDescription>
                    Create a new agent to add to the simulation
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="agent-name">Name</Label>
                    <Input
                      id="agent-name"
                      value={newAgent.name}
                      onChange={(e) => setNewAgent(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter agent name"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="agent-role">Role</Label>
                    <Select
                      value={newAgent.role}
                      onValueChange={(value) => setNewAgent(prev => ({ ...prev, role: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select role" />
                      </SelectTrigger>
                      <SelectContent>
                        {agentRoles.map(role => (
                          <SelectItem key={role} value={role}>
                            {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="agent-x">X Position</Label>
                      <Input
                        id="agent-x"
                        type="number"
                        value={newAgent.x}
                        onChange={(e) => setNewAgent(prev => ({ ...prev, x: parseFloat(e.target.value) || 0 }))}
                        step="0.1"
                      />
                    </div>
                    <div>
                      <Label htmlFor="agent-y">Y Position</Label>
                      <Input
                        id="agent-y"
                        type="number"
                        value={newAgent.y}
                        onChange={(e) => setNewAgent(prev => ({ ...prev, y: parseFloat(e.target.value) || 0 }))}
                        step="0.1"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="agent-location">Starting Location (Optional)</Label>
                    <Select
                      value={newAgent.current_location_id?.toString() || ''}
                      onValueChange={(value) => setNewAgent(prev => ({ 
                        ...prev, 
                        current_location_id: value ? parseInt(value) : null 
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select location" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">No specific location</SelectItem>
                        {locations.map(location => (
                          <SelectItem key={location.id} value={location.id.toString()}>
                            {location.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex justify-end space-x-2">
                    <Button variant="outline" onClick={() => setShowAddDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleAddAgent}>
                      Add Agent
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="search">Search</Label>
              <Input
                id="search"
                placeholder="Search agents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div>
              <Label htmlFor="role-filter">Filter by Role</Label>
              <Select value={filterRole} onValueChange={setFilterRole}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Roles</SelectItem>
                  {agentRoles.map(role => (
                    <SelectItem key={role} value={role}>
                      {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="status-filter">Filter by Status</Label>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="idle">Idle</SelectItem>
                  <SelectItem value="moving">Moving</SelectItem>
                  <SelectItem value="working">Working</SelectItem>
                  <SelectItem value="eating">Eating</SelectItem>
                  <SelectItem value="sleeping">Sleeping</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Agent List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filteredAgents.map(agent => (
          <Card 
            key={agent.id} 
            className={`cursor-pointer transition-all hover:shadow-md ${
              selectedAgent?.id === agent.id ? 'ring-2 ring-blue-500' : ''
            }`}
            onClick={() => onAgentSelect(agent)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center space-x-2">
                  <div className={`w-3 h-3 rounded-full ${getRoleColor(agent.role)}`}></div>
                  <span>{agent.name}</span>
                </CardTitle>
                <Badge variant={getStatusColor(agent.status)}>
                  {agent.status}
                </Badge>
              </div>
              <CardDescription>
                {agent.role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Health and Energy */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <Heart className="h-3 w-3 text-red-500" />
                    <span className="text-xs">Health</span>
                  </div>
                  <span className="text-xs font-medium">{agent.health.toFixed(1)}%</span>
                </div>
                <Progress value={agent.health} className="h-1" />
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <Zap className="h-3 w-3 text-yellow-500" />
                    <span className="text-xs">Energy</span>
                  </div>
                  <span className="text-xs font-medium">{agent.energy.toFixed(1)}%</span>
                </div>
                <Progress value={agent.energy} className="h-1" />
              </div>

              {/* Location */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-1">
                  <MapPin className="h-3 w-3 text-blue-500" />
                  <span className="text-xs">Location</span>
                </div>
                <span className="text-xs">
                  {agent.current_location_id 
                    ? locations.find(loc => loc.id === agent.current_location_id)?.name || 'Unknown'
                    : `(${agent.x.toFixed(1)}, ${agent.y.toFixed(1)})`
                  }
                </span>
              </div>

              {/* Current Activity */}
              {agent.status !== 'idle' && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <Activity className="h-3 w-3 text-green-500" />
                    <span className="text-xs">Activity</span>
                  </div>
                  <span className="text-xs capitalize">
                    {agent.status.replace('_', ' ')}
                  </span>
                </div>
              )}

              {/* Schedule Info */}
              {agent.schedule && Object.keys(agent.schedule).length > 0 && (
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-1">
                    <Clock className="h-3 w-3 text-purple-500" />
                    <span className="text-xs">Scheduled</span>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {Object.keys(agent.schedule).length} activities
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredAgents.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">
              {agents.length === 0 
                ? "No agents in the simulation. Add some agents to get started!"
                : "No agents match your current filters."
              }
            </p>
          </CardContent>
        </Card>
      )}

      {/* Selected Agent Details */}
      {selectedAgent && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <div className={`w-4 h-4 rounded-full ${getRoleColor(selectedAgent.role)}`}></div>
              <span>{selectedAgent.name}</span>
            </CardTitle>
            <CardDescription>Detailed agent information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-xs text-muted-foreground">Role</Label>
                <p className="text-sm capitalize">
                  {selectedAgent.role.replace('_', ' ')}
                </p>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Status</Label>
                <Badge variant={getStatusColor(selectedAgent.status)}>
                  {selectedAgent.status}
                </Badge>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Position</Label>
                <p className="text-sm font-mono">
                  ({selectedAgent.x.toFixed(2)}, {selectedAgent.y.toFixed(2)})
                </p>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">ID</Label>
                <p className="text-sm font-mono">#{selectedAgent.id}</p>
              </div>
            </div>

            {selectedAgent.preferences && Object.keys(selectedAgent.preferences).length > 0 && (
              <div>
                <Label className="text-xs text-muted-foreground">Preferences</Label>
                <div className="mt-1 space-y-1">
                  {Object.entries(selectedAgent.preferences).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="capitalize">{key.replace('_', ' ')}</span>
                      <span>{typeof value === 'number' ? value.toFixed(2) : value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default AgentPanel

