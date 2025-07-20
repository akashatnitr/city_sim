import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Cloud, CloudRain, CloudSnow, Sun, CloudDrizzle, Zap, Eye, Wind, Thermometer, Droplets } from 'lucide-react'

const WeatherPanel = ({ weather }) => {
  if (!weather) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Cloud className="h-5 w-5" />
            <span>Weather</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">No weather data available</p>
        </CardContent>
      </Card>
    )
  }

  const getWeatherIcon = (condition) => {
    const icons = {
      clear: Sun,
      cloudy: Cloud,
      rain: CloudRain,
      storm: Zap,
      snow: CloudSnow,
      fog: CloudDrizzle
    }
    return icons[condition] || Cloud
  }

  const getWeatherColor = (condition) => {
    const colors = {
      clear: 'text-yellow-500',
      cloudy: 'text-gray-500',
      rain: 'text-blue-500',
      storm: 'text-purple-500',
      snow: 'text-blue-200',
      fog: 'text-gray-400'
    }
    return colors[condition] || 'text-gray-500'
  }

  const getConditionBadge = (condition) => {
    const variants = {
      clear: 'default',
      cloudy: 'secondary',
      rain: 'default',
      storm: 'destructive',
      snow: 'secondary',
      fog: 'secondary'
    }
    return variants[condition] || 'secondary'
  }

  const getTemperatureColor = (temp) => {
    if (temp < 0) return 'text-blue-600'
    if (temp < 10) return 'text-blue-500'
    if (temp < 20) return 'text-green-500'
    if (temp < 30) return 'text-yellow-500'
    return 'text-red-500'
  }

  const WeatherIcon = getWeatherIcon(weather.condition)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <WeatherIcon className={`h-5 w-5 ${getWeatherColor(weather.condition)}`} />
          <span>Weather</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Current Condition */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Condition</span>
          <Badge variant={getConditionBadge(weather.condition)}>
            {weather.condition.charAt(0).toUpperCase() + weather.condition.slice(1)}
          </Badge>
        </div>

        {/* Temperature */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <Thermometer className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Temperature</span>
          </div>
          <span className={`text-sm font-medium ${getTemperatureColor(weather.temperature)}`}>
            {weather.temperature.toFixed(1)}°C
          </span>
        </div>

        {/* Humidity */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <Droplets className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-muted-foreground">Humidity</span>
          </div>
          <span className="text-sm font-medium">
            {weather.humidity?.toFixed(1) || 0}%
          </span>
        </div>

        {/* Wind Speed */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <Wind className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-muted-foreground">Wind</span>
          </div>
          <span className="text-sm font-medium">
            {weather.wind_speed?.toFixed(1) || 0} km/h
          </span>
        </div>

        {/* Visibility */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-1">
            <Eye className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-muted-foreground">Visibility</span>
          </div>
          <span className="text-sm font-medium">
            {weather.visibility?.toFixed(1) || 10} km
          </span>
        </div>

        {/* Precipitation */}
        {weather.precipitation > 0 && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1">
              <CloudRain className="h-4 w-4 text-blue-500" />
              <span className="text-sm text-muted-foreground">Precipitation</span>
            </div>
            <span className="text-sm font-medium">
              {weather.precipitation.toFixed(1)} mm/h
            </span>
          </div>
        )}

        {/* Weather Effects */}
        {weather.condition !== 'clear' && (
          <div className="pt-2 border-t">
            <div className="text-xs text-muted-foreground mb-2">Effects on Simulation</div>
            <div className="space-y-1">
              {weather.condition === 'rain' && (
                <div className="text-xs">• Reduced movement speed</div>
              )}
              {weather.condition === 'storm' && (
                <>
                  <div className="text-xs">• Significantly reduced movement</div>
                  <div className="text-xs">• Increased energy consumption</div>
                </>
              )}
              {weather.condition === 'snow' && (
                <>
                  <div className="text-xs">• Reduced movement speed</div>
                  <div className="text-xs">• Some locations may close</div>
                </>
              )}
              {weather.condition === 'fog' && (
                <div className="text-xs">• Reduced visibility affects navigation</div>
              )}
              {weather.temperature < 0 && (
                <div className="text-xs">• Increased energy consumption</div>
              )}
              {weather.temperature > 35 && (
                <div className="text-xs">• Heat stress affects agents</div>
              )}
            </div>
          </div>
        )}

        {/* Weather Severity Indicator */}
        {(weather.condition === 'storm' || weather.wind_speed > 40 || weather.precipitation > 25 || weather.visibility < 1) && (
          <div className="pt-2 border-t">
            <Badge variant="destructive" className="w-full justify-center">
              ⚠️ Severe Weather Warning
            </Badge>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default WeatherPanel

