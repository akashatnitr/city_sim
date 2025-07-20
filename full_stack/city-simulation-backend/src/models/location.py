from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
import json
from datetime import datetime

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # home, office, school, restaurant, etc.
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer, default=100)
    current_occupancy = db.Column(db.Integer, default=0)
    is_open = db.Column(db.Boolean, default=True)
    opening_hours = db.Column(db.Text)  # JSON string of opening hours
    services = db.Column(db.Text)  # JSON string of available services
    properties = db.Column(db.Text)  # JSON string of additional properties
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Location {self.name} ({self.type})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'x': self.x,
            'y': self.y,
            'capacity': self.capacity,
            'current_occupancy': self.current_occupancy,
            'is_open': self.is_open,
            'opening_hours': json.loads(self.opening_hours) if self.opening_hours else {},
            'services': json.loads(self.services) if self.services else [],
            'properties': json.loads(self.properties) if self.properties else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def set_opening_hours(self, hours_dict):
        self.opening_hours = json.dumps(hours_dict)

    def get_opening_hours(self):
        return json.loads(self.opening_hours) if self.opening_hours else {}

    def set_services(self, services_list):
        self.services = json.dumps(services_list)

    def get_services(self):
        return json.loads(self.services) if self.services else []

    def set_properties(self, properties_dict):
        self.properties = json.dumps(properties_dict)

    def get_properties(self):
        return json.loads(self.properties) if self.properties else {}

    def is_at_capacity(self):
        return self.current_occupancy >= self.capacity

    def can_accommodate(self, count=1):
        return self.current_occupancy + count <= self.capacity

class Road(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    from_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    to_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    distance = db.Column(db.Float, nullable=False)  # in kilometers
    speed_limit = db.Column(db.Float, default=50.0)  # km/h
    current_traffic = db.Column(db.Float, default=1.0)  # traffic multiplier (1.0 = normal)
    road_type = db.Column(db.String(50), default='street')  # highway, street, path, etc.
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    from_location = db.relationship('Location', foreign_keys=[from_location_id], backref='outgoing_roads')
    to_location = db.relationship('Location', foreign_keys=[to_location_id], backref='incoming_roads')

    def __repr__(self):
        return f'<Road {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'from_location_id': self.from_location_id,
            'to_location_id': self.to_location_id,
            'distance': self.distance,
            'speed_limit': self.speed_limit,
            'current_traffic': self.current_traffic,
            'road_type': self.road_type,
            'is_blocked': self.is_blocked,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_travel_time(self, transport_mode='walking'):
        """Calculate travel time based on transport mode and current conditions"""
        base_speed = {
            'walking': 5.0,  # km/h
            'cycling': 15.0,
            'car': min(self.speed_limit, 60.0),
            'bus': min(self.speed_limit * 0.8, 40.0),
            'metro': 80.0
        }.get(transport_mode, 5.0)
        
        if self.is_blocked:
            return float('inf')
        
        effective_speed = base_speed / self.current_traffic
        return (self.distance / effective_speed) * 60  # return in minutes

class TransitStop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # bus_stop, metro_station, etc.
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    routes = db.Column(db.Text)  # JSON string of route information
    schedule = db.Column(db.Text)  # JSON string of schedule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    location = db.relationship('Location', backref='transit_stops')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'location_id': self.location_id,
            'routes': json.loads(self.routes) if self.routes else [],
            'schedule': json.loads(self.schedule) if self.schedule else {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def set_routes(self, routes_list):
        self.routes = json.dumps(routes_list)

    def get_routes(self):
        return json.loads(self.routes) if self.routes else []

    def set_schedule(self, schedule_dict):
        self.schedule = json.dumps(schedule_dict)

    def get_schedule(self):
        return json.loads(self.schedule) if self.schedule else {}

