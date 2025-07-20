from flask import Blueprint, jsonify, request, current_app
from src.models.user import db
from src.models.event import SimulationState, Event, WeatherCondition, SimulationLog
from src.models.location import Location, Road, TransitStop
from src.simulation.data_initializer import DataInitializer
from datetime import datetime, timedelta
import json

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/simulation/state', methods=['GET'])
def get_simulation_state():
    """Get current simulation state"""
    state = SimulationState.query.filter_by(name='main').first()
    if not state:
        # Create default simulation state
        state = SimulationState(
            name='main',
            is_running=False,
            current_time=datetime.utcnow(),
            time_acceleration=1.0,
            weather_condition='clear',
            temperature=20.0
        )
        db.session.add(state)
        db.session.commit()
    
    return jsonify(state.to_dict())

@simulation_bp.route('/simulation/start', methods=['POST'])
def start_simulation():
    """Start the simulation"""
    data = request.json or {}
    
    state = SimulationState.query.filter_by(name='main').first()
    if not state:
        state = SimulationState(name='main')
        db.session.add(state)
    
    state.is_running = True
    state.time_acceleration = data.get('time_acceleration', 1.0)
    state.current_time = datetime.utcnow()
    
    if 'settings' in data:
        state.set_settings(data['settings'])
    
    db.session.commit()
    
    # Start the simulation engine
    if hasattr(current_app, 'simulation_engine'):
        current_app.simulation_engine.start_simulation(data)
    
    return jsonify({'message': 'Simulation started', 'state': state.to_dict()})

@simulation_bp.route('/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop the simulation"""
    state = SimulationState.query.filter_by(name='main').first()
    if state:
        state.is_running = False
        db.session.commit()
    
    # Stop the simulation engine
    if hasattr(current_app, 'simulation_engine'):
        current_app.simulation_engine.stop_simulation()
    
    return jsonify({'message': 'Simulation stopped'})

@simulation_bp.route('/simulation/settings', methods=['GET', 'PUT'])
def simulation_settings():
    """Get or update simulation settings"""
    state = SimulationState.query.filter_by(name='main').first()
    if not state:
        state = SimulationState(name='main')
        db.session.add(state)
        db.session.commit()
    
    if request.method == 'GET':
        return jsonify(state.get_settings())
    
    elif request.method == 'PUT':
        data = request.json
        state.set_settings(data)
        state.time_acceleration = data.get('time_acceleration', state.time_acceleration)
        db.session.commit()
        return jsonify({'message': 'Settings updated', 'settings': state.get_settings()})

@simulation_bp.route('/simulation/statistics', methods=['GET'])
def get_simulation_statistics():
    """Get simulation statistics"""
    state = SimulationState.query.filter_by(name='main').first()
    if not state:
        return jsonify({})
    
    return jsonify(state.get_statistics())

@simulation_bp.route('/simulation/events', methods=['GET', 'POST'])
def simulation_events():
    """Get all events or create a new event"""
    if request.method == 'GET':
        events = Event.query.filter_by(is_active=True).all()
        return jsonify([event.to_dict() for event in events])
    
    elif request.method == 'POST':
        data = request.json
        event = Event(
            name=data['name'],
            type=data['type'],
            severity=data.get('severity', 'low'),
            start_time=datetime.fromisoformat(data['start_time'].replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(data['end_time'].replace('Z', '+00:00')) if data.get('end_time') else None,
            location_id=data.get('location_id'),
            description=data.get('description', '')
        )
        
        if 'affected_area' in data:
            event.set_affected_area(data['affected_area'])
        if 'effects' in data:
            event.set_effects(data['effects'])
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify(event.to_dict()), 201

@simulation_bp.route('/simulation/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
def simulation_event(event_id):
    """Get, update, or delete a specific event"""
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'GET':
        return jsonify(event.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        event.name = data.get('name', event.name)
        event.type = data.get('type', event.type)
        event.severity = data.get('severity', event.severity)
        event.description = data.get('description', event.description)
        event.is_active = data.get('is_active', event.is_active)
        
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if 'end_time' in data:
            event.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        if 'affected_area' in data:
            event.set_affected_area(data['affected_area'])
        if 'effects' in data:
            event.set_effects(data['effects'])
        
        db.session.commit()
        return jsonify(event.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(event)
        db.session.commit()
        return '', 204

@simulation_bp.route('/simulation/weather', methods=['GET', 'POST'])
def weather_conditions():
    """Get current weather or create new weather condition"""
    if request.method == 'GET':
        current_weather = WeatherCondition.query.filter(
            WeatherCondition.start_time <= datetime.utcnow(),
            (WeatherCondition.end_time.is_(None)) | (WeatherCondition.end_time > datetime.utcnow())
        ).first()
        
        if current_weather:
            return jsonify(current_weather.to_dict())
        else:
            return jsonify({'condition': 'clear', 'temperature': 20.0})
    
    elif request.method == 'POST':
        data = request.json
        weather = WeatherCondition(
            condition=data['condition'],
            temperature=data['temperature'],
            humidity=data.get('humidity', 50.0),
            wind_speed=data.get('wind_speed', 0.0),
            visibility=data.get('visibility', 10.0),
            start_time=datetime.fromisoformat(data['start_time'].replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(data['end_time'].replace('Z', '+00:00')) if data.get('end_time') else None
        )
        
        if 'effects' in data:
            weather.set_effects(data['effects'])
        
        db.session.add(weather)
        db.session.commit()
        
        return jsonify(weather.to_dict()), 201

@simulation_bp.route('/simulation/locations', methods=['GET', 'POST'])
def locations():
    """Get all locations or create a new location"""
    if request.method == 'GET':
        locations = Location.query.all()
        return jsonify([location.to_dict() for location in locations])
    
    elif request.method == 'POST':
        data = request.json
        location = Location(
            name=data['name'],
            type=data['type'],
            x=data['x'],
            y=data['y'],
            capacity=data.get('capacity', 100),
            is_open=data.get('is_open', True)
        )
        
        if 'opening_hours' in data:
            location.set_opening_hours(data['opening_hours'])
        if 'services' in data:
            location.set_services(data['services'])
        if 'properties' in data:
            location.set_properties(data['properties'])
        
        db.session.add(location)
        db.session.commit()
        
        return jsonify(location.to_dict()), 201

@simulation_bp.route('/simulation/locations/<int:location_id>', methods=['GET', 'PUT', 'DELETE'])
def location(location_id):
    """Get, update, or delete a specific location"""
    location = Location.query.get_or_404(location_id)
    
    if request.method == 'GET':
        return jsonify(location.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        location.name = data.get('name', location.name)
        location.type = data.get('type', location.type)
        location.x = data.get('x', location.x)
        location.y = data.get('y', location.y)
        location.capacity = data.get('capacity', location.capacity)
        location.is_open = data.get('is_open', location.is_open)
        
        if 'opening_hours' in data:
            location.set_opening_hours(data['opening_hours'])
        if 'services' in data:
            location.set_services(data['services'])
        if 'properties' in data:
            location.set_properties(data['properties'])
        
        db.session.commit()
        return jsonify(location.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(location)
        db.session.commit()
        return '', 204

@simulation_bp.route('/simulation/roads', methods=['GET', 'POST'])
def roads():
    """Get all roads or create a new road"""
    if request.method == 'GET':
        roads = Road.query.all()
        return jsonify([road.to_dict() for road in roads])
    
    elif request.method == 'POST':
        data = request.json
        road = Road(
            name=data['name'],
            from_location_id=data['from_location_id'],
            to_location_id=data['to_location_id'],
            distance=data['distance'],
            speed_limit=data.get('speed_limit', 50.0),
            road_type=data.get('road_type', 'street'),
            is_blocked=data.get('is_blocked', False)
        )
        
        db.session.add(road)
        db.session.commit()
        
        return jsonify(road.to_dict()), 201

@simulation_bp.route('/simulation/logs', methods=['GET'])
def get_simulation_logs():
    """Get simulation logs"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 100, type=int)
    log_type = request.args.get('type')
    
    query = SimulationLog.query
    if log_type:
        query = query.filter_by(log_type=log_type)
    
    logs = query.order_by(SimulationLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    })

@simulation_bp.route('/simulation/initialize', methods=['POST'])
def initialize_simulation():
    """Initialize simulation with sample data"""
    data = request.json or {}
    city_size = data.get('city_size', 'medium')
    
    try:
        initializer = DataInitializer()
        initializer.initialize_city(city_size)
        
        summary = initializer.get_initialization_summary()
        
        return jsonify({
            'message': 'Simulation initialized successfully',
            'summary': summary
        }), 201
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to initialize simulation: {str(e)}'
        }), 500

