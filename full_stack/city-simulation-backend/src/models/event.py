from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
import json
from datetime import datetime

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # weather, emergency, holiday, festival, etc.
    severity = db.Column(db.String(20), default='low')  # low, medium, high, critical
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))  # null for city-wide events
    affected_area = db.Column(db.Text)  # JSON string of affected coordinates/areas
    effects = db.Column(db.Text)  # JSON string of event effects
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    location = db.relationship('Location', backref='events')

    def __repr__(self):
        return f'<Event {self.name} ({self.type})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'severity': self.severity,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'location_id': self.location_id,
            'affected_area': json.loads(self.affected_area) if self.affected_area else {},
            'effects': json.loads(self.effects) if self.effects else {},
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def set_affected_area(self, area_dict):
        self.affected_area = json.dumps(area_dict)

    def get_affected_area(self):
        return json.loads(self.affected_area) if self.affected_area else {}

    def set_effects(self, effects_dict):
        self.effects = json.dumps(effects_dict)

    def get_effects(self):
        return json.loads(self.effects) if self.effects else {}

class SimulationState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    is_running = db.Column(db.Boolean, default=False)
    current_time = db.Column(db.DateTime, default=datetime.utcnow)
    time_acceleration = db.Column(db.Float, default=1.0)  # 1.0 = real time, 60.0 = 1 minute = 1 hour
    total_agents = db.Column(db.Integer, default=0)
    active_agents = db.Column(db.Integer, default=0)
    total_events = db.Column(db.Integer, default=0)
    active_events = db.Column(db.Integer, default=0)
    weather_condition = db.Column(db.String(50), default='clear')
    temperature = db.Column(db.Float, default=20.0)  # Celsius
    settings = db.Column(db.Text)  # JSON string of simulation settings
    statistics = db.Column(db.Text)  # JSON string of simulation statistics
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SimulationState {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_running': self.is_running,
            'current_time': self.current_time.isoformat() if self.current_time else None,
            'time_acceleration': self.time_acceleration,
            'total_agents': self.total_agents,
            'active_agents': self.active_agents,
            'total_events': self.total_events,
            'active_events': self.active_events,
            'weather_condition': self.weather_condition,
            'temperature': self.temperature,
            'settings': json.loads(self.settings) if self.settings else {},
            'statistics': json.loads(self.statistics) if self.statistics else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def set_settings(self, settings_dict):
        self.settings = json.dumps(settings_dict)

    def get_settings(self):
        return json.loads(self.settings) if self.settings else {}

    def set_statistics(self, stats_dict):
        self.statistics = json.dumps(stats_dict)

    def get_statistics(self):
        return json.loads(self.statistics) if self.statistics else {}

class WeatherCondition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    condition = db.Column(db.String(50), nullable=False)  # clear, rain, snow, storm, etc.
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, default=50.0)
    wind_speed = db.Column(db.Float, default=0.0)
    visibility = db.Column(db.Float, default=10.0)  # km
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    effects = db.Column(db.Text)  # JSON string of weather effects on agents/traffic
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'condition': self.condition,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'wind_speed': self.wind_speed,
            'visibility': self.visibility,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'effects': json.loads(self.effects) if self.effects else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def set_effects(self, effects_dict):
        self.effects = json.dumps(effects_dict)

    def get_effects(self):
        return json.loads(self.effects) if self.effects else {}

class SimulationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulation_state.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    log_type = db.Column(db.String(50), nullable=False)  # agent_action, event, system, etc.
    entity_id = db.Column(db.Integer)  # agent_id, event_id, etc.
    entity_type = db.Column(db.String(50))  # agent, event, location, etc.
    action = db.Column(db.String(100))
    details = db.Column(db.Text)  # JSON string of additional details
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    simulation = db.relationship('SimulationState', backref='logs')

    def to_dict(self):
        return {
            'id': self.id,
            'simulation_id': self.simulation_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'log_type': self.log_type,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'action': self.action,
            'details': json.loads(self.details) if self.details else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def set_details(self, details_dict):
        self.details = json.dumps(details_dict)

    def get_details(self):
        return json.loads(self.details) if self.details else {}

