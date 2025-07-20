from flask_sqlalchemy import SQLAlchemy
from src.models.user import db
import json
from datetime import datetime

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # student, engineer, teacher, etc.
    x = db.Column(db.Float, nullable=False, default=0.0)
    y = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(50), default='idle')  # idle, moving, working, etc.
    energy = db.Column(db.Float, default=100.0)
    health = db.Column(db.Float, default=100.0)
    current_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    target_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    schedule = db.Column(db.Text)  # JSON string of daily schedule
    preferences = db.Column(db.Text)  # JSON string of agent preferences
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    current_location = db.relationship('Location', foreign_keys=[current_location_id], backref='current_agents')
    target_location = db.relationship('Location', foreign_keys=[target_location_id])
    movements = db.relationship('AgentMovement', backref='agent', lazy=True)
    activities = db.relationship('AgentActivity', backref='agent', lazy=True)

    def __repr__(self):
        return f'<Agent {self.name} ({self.role})>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'x': self.x,
            'y': self.y,
            'status': self.status,
            'energy': self.energy,
            'health': self.health,
            'current_location_id': self.current_location_id,
            'target_location_id': self.target_location_id,
            'schedule': json.loads(self.schedule) if self.schedule else {},
            'preferences': json.loads(self.preferences) if self.preferences else {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def set_schedule(self, schedule_dict):
        self.schedule = json.dumps(schedule_dict)

    def get_schedule(self):
        return json.loads(self.schedule) if self.schedule else {}

    def set_preferences(self, preferences_dict):
        self.preferences = json.dumps(preferences_dict)

    def get_preferences(self):
        return json.loads(self.preferences) if self.preferences else {}

class AgentMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    from_x = db.Column(db.Float, nullable=False)
    from_y = db.Column(db.Float, nullable=False)
    to_x = db.Column(db.Float, nullable=False)
    to_y = db.Column(db.Float, nullable=False)
    from_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    to_location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    distance = db.Column(db.Float)
    transport_mode = db.Column(db.String(50), default='walking')  # walking, car, bus, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'from_x': self.from_x,
            'from_y': self.from_y,
            'to_x': self.to_x,
            'to_y': self.to_y,
            'from_location_id': self.from_location_id,
            'to_location_id': self.to_location_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'distance': self.distance,
            'transport_mode': self.transport_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AgentActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    activity_type = db.Column(db.String(100), nullable=False)  # work, eat, sleep, shop, etc.
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in minutes
    energy_cost = db.Column(db.Float, default=0.0)
    satisfaction = db.Column(db.Float, default=0.0)  # 0-100 scale
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    location = db.relationship('Location', backref='activities')

    def to_dict(self):
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'activity_type': self.activity_type,
            'location_id': self.location_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'energy_cost': self.energy_cost,
            'satisfaction': self.satisfaction,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

