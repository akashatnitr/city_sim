import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Play, Pause, Square, Settings, Users, MapPin, Activity, Cloud, AlertTriangle } from 'lucide-react'
import CityMap from './components/CityMap.jsx'
import AgentPanel from './components/AgentPanel.jsx'
import ControlPanel from './components/ControlPanel.jsx'
import StatisticsPanel from './components/StatisticsPanel.jsx'
import EventsPanel from './components/EventsPanel.jsx'
import WeatherPanel from './components/WeatherPanel.jsx'
import { useSimulation } from './hooks/useSimulation.js'
import './App.css'

function App() {
  const {
    simulationState,
    agents,
    locations,
    events,
    weather,
    isConnected,
    startSimulation,
    stopSimulation,
    addAgent,
    initializeCity
  } = useSimulation()

  const [activeTab, setActiveTab] = useState('map')
  const [selectedAgent, setSelectedAgent] = useState(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm dark:bg-slate-900/80 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <MapPin className="h-8 w-8 text-blue-600" />
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                  City Simulation System
                </h1>
              </div>
              <Badge variant={isConnected ? "default" : "destructive"}>
                {isConnected ? "Connected" : "Disconnected"}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant={simulationState?.is_running ? "destructive" : "default"}
                onClick={simulationState?.is_running ? stopSimulation : startSimulation}
                className="flex items-center space-x-2"
              >
                {simulationState?.is_running ? (
                  <>
                    <Pause className="h-4 w-4" />
                    <span>Stop</span>
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    <span>Start</span>
                  </>
                )}
              </Button>
              
              <Button variant="outline" onClick={() => initializeCity('medium')}>
                <Settings className="h-4 w-4 mr-2" />
                Initialize City
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Sidebar - Statistics */}
          <div className="lg:col-span-1 space-y-6">
            <StatisticsPanel 
              simulationState={simulationState}
              agents={agents}
              locations={locations}
              events={events}
            />
            
            <WeatherPanel weather={weather} />
            
            <EventsPanel events={events} />
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="map" className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4" />
                  <span>Map</span>
                </TabsTrigger>
                <TabsTrigger value="agents" className="flex items-center space-x-2">
                  <Users className="h-4 w-4" />
                  <span>Agents</span>
                </TabsTrigger>
                <TabsTrigger value="control" className="flex items-center space-x-2">
                  <Settings className="h-4 w-4" />
                  <span>Control</span>
                </TabsTrigger>
                <TabsTrigger value="analytics" className="flex items-center space-x-2">
                  <Activity className="h-4 w-4" />
                  <span>Analytics</span>
                </TabsTrigger>
              </TabsList>

              <TabsContent value="map" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <MapPin className="h-5 w-5" />
                      <span>City Map</span>
                    </CardTitle>
                    <CardDescription>
                      Real-time visualization of agents, locations, and events
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <CityMap
                      agents={agents}
                      locations={locations}
                      events={events}
                      weather={weather}
                      onAgentSelect={setSelectedAgent}
                      selectedAgent={selectedAgent}
                    />
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="agents" className="space-y-6">
                <AgentPanel
                  agents={agents}
                  locations={locations}
                  onAgentSelect={setSelectedAgent}
                  selectedAgent={selectedAgent}
                  onAddAgent={addAgent}
                />
              </TabsContent>

              <TabsContent value="control" className="space-y-6">
                <ControlPanel
                  simulationState={simulationState}
                  onStartSimulation={startSimulation}
                  onStopSimulation={stopSimulation}
                  onInitializeCity={initializeCity}
                />
              </TabsContent>

              <TabsContent value="analytics" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Agent Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center text-muted-foreground">
                        Analytics charts will be displayed here
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardHeader>
                      <CardTitle>Traffic Patterns</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center text-muted-foreground">
                        Traffic analysis charts will be displayed here
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </main>

      {/* Status Bar */}
      <footer className="border-t bg-white/80 backdrop-blur-sm dark:bg-slate-900/80 mt-8">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center space-x-4">
              <span>
                Simulation Time: {simulationState?.current_time ? 
                  new Date(simulationState.current_time).toLocaleString() : 'Not started'}
              </span>
              <span>
                Speed: {simulationState?.time_acceleration || 1}x
              </span>
            </div>
            
            <div className="flex items-center space-x-4">
              <span>Agents: {agents?.length || 0}</span>
              <span>Locations: {locations?.length || 0}</span>
              <span>Active Events: {events?.filter(e => e.is_active)?.length || 0}</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App

