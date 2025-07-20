from flask import Blueprint, jsonify, request, current_app
from src.models.user import db
from src.models.agent import Agent, AgentMovement, AgentActivity
from src.models.location import Location
from datetime import datetime
import json

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('/agents', methods=['GET', 'POST'])
def agents():
    """Get all agents or create a new agent"""
    if request.method == 'GET':
        role = request.args.get('role')
        status = request.args.get('status')
        location_id = request.args.get('location_id', type=int)
        
        query = Agent.query
        if role:
            query = query.filter_by(role=role)
        if status:
            query = query.filter_by(status=status)
        if location_id:
            query = query.filter_by(current_location_id=location_id)
        
        agents = query.all()
        return jsonify([agent.to_dict() for agent in agents])
    
    elif request.method == 'POST':
        data = request.json
        agent = Agent(
            name=data['name'],
            role=data['role'],
            x=data.get('x', 0.0),
            y=data.get('y', 0.0),
            status=data.get('status', 'idle'),
            energy=data.get('energy', 100.0),
            health=data.get('health', 100.0),
            current_location_id=data.get('current_location_id')
        )
        
        if 'schedule' in data:
            agent.set_schedule(data['schedule'])
        if 'preferences' in data:
            agent.set_preferences(data['preferences'])
        
        db.session.add(agent)
        db.session.commit()
        
        # Notify via WebSocket if simulation engine is available
        if hasattr(current_app, 'simulation_engine'):
            current_app.simulation_engine.add_agent(agent.to_dict())
        
        return jsonify(agent.to_dict()), 201

@agents_bp.route('/agents/<int:agent_id>', methods=['GET', 'PUT', 'DELETE'])
def agent(agent_id):
    """Get, update, or delete a specific agent"""
    agent = Agent.query.get_or_404(agent_id)
    
    if request.method == 'GET':
        return jsonify(agent.to_dict())
    
    elif request.method == 'PUT':
        data = request.json
        agent.name = data.get('name', agent.name)
        agent.role = data.get('role', agent.role)
        agent.x = data.get('x', agent.x)
        agent.y = data.get('y', agent.y)
        agent.status = data.get('status', agent.status)
        agent.energy = data.get('energy', agent.energy)
        agent.health = data.get('health', agent.health)
        agent.current_location_id = data.get('current_location_id', agent.current_location_id)
        agent.target_location_id = data.get('target_location_id', agent.target_location_id)
        
        if 'schedule' in data:
            agent.set_schedule(data['schedule'])
        if 'preferences' in data:
            agent.set_preferences(data['preferences'])
        
        db.session.commit()
        return jsonify(agent.to_dict())
    
    elif request.method == 'DELETE':
        db.session.delete(agent)
        db.session.commit()
        return '', 204

@agents_bp.route('/agents/<int:agent_id>/move', methods=['POST'])
def move_agent(agent_id):
    """Move an agent to a new location"""
    agent = Agent.query.get_or_404(agent_id)
    data = request.json
    
    # Record the movement
    movement = AgentMovement(
        agent_id=agent.id,
        from_x=agent.x,
        from_y=agent.y,
        to_x=data['x'],
        to_y=data['y'],
        from_location_id=agent.current_location_id,
        to_location_id=data.get('location_id'),
        start_time=datetime.utcnow(),
        transport_mode=data.get('transport_mode', 'walking')
    )
    
    # Update agent position
    agent.x = data['x']
    agent.y = data['y']
    agent.status = 'moving'
    if data.get('location_id'):
        agent.current_location_id = data['location_id']
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify({
        'message': 'Agent moved successfully',
        'agent': agent.to_dict(),
        'movement': movement.to_dict()
    })

@agents_bp.route('/agents/<int:agent_id>/activity', methods=['POST'])
def start_activity(agent_id):
    """Start a new activity for an agent"""
    agent = Agent.query.get_or_404(agent_id)
    data = request.json
    
    activity = AgentActivity(
        agent_id=agent.id,
        activity_type=data['activity_type'],
        location_id=data.get('location_id', agent.current_location_id),
        start_time=datetime.utcnow(),
        duration=data.get('duration'),
        energy_cost=data.get('energy_cost', 0.0)
    )
    
    agent.status = data['activity_type']
    agent.energy = max(0, agent.energy - activity.energy_cost)
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({
        'message': 'Activity started',
        'agent': agent.to_dict(),
        'activity': activity.to_dict()
    })

@agents_bp.route('/agents/<int:agent_id>/activities', methods=['GET'])
def get_agent_activities(agent_id):
    """Get all activities for a specific agent"""
    agent = Agent.query.get_or_404(agent_id)
    activities = AgentActivity.query.filter_by(agent_id=agent_id).order_by(AgentActivity.start_time.desc()).all()
    
    return jsonify([activity.to_dict() for activity in activities])

@agents_bp.route('/agents/<int:agent_id>/movements', methods=['GET'])
def get_agent_movements(agent_id):
    """Get all movements for a specific agent"""
    agent = Agent.query.get_or_404(agent_id)
    movements = AgentMovement.query.filter_by(agent_id=agent_id).order_by(AgentMovement.start_time.desc()).all()
    
    return jsonify([movement.to_dict() for movement in movements])

@agents_bp.route('/agents/<int:agent_id>/schedule', methods=['GET', 'PUT'])
def agent_schedule(agent_id):
    """Get or update an agent's schedule"""
    agent = Agent.query.get_or_404(agent_id)
    
    if request.method == 'GET':
        return jsonify(agent.get_schedule())
    
    elif request.method == 'PUT':
        data = request.json
        agent.set_schedule(data)
        db.session.commit()
        return jsonify({'message': 'Schedule updated', 'schedule': agent.get_schedule()})

@agents_bp.route('/agents/<int:agent_id>/preferences', methods=['GET', 'PUT'])
def agent_preferences(agent_id):
    """Get or update an agent's preferences"""
    agent = Agent.query.get_or_404(agent_id)
    
    if request.method == 'GET':
        return jsonify(agent.get_preferences())
    
    elif request.method == 'PUT':
        data = request.json
        agent.set_preferences(data)
        db.session.commit()
        return jsonify({'message': 'Preferences updated', 'preferences': agent.get_preferences()})

@agents_bp.route('/agents/roles', methods=['GET'])
def get_agent_roles():
    """Get all available agent roles"""
    roles = [
        'student',
        'software_engineer',
        'teacher',
        'restaurant_staff',
        'restaurant_customer',
        'grocery_worker',
        'grocery_shopper',
        'delivery_personnel',
        'citizen',
        'police_officer',
        'firefighter',
        'doctor',
        'nurse',
        'bus_driver',
        'taxi_driver'
    ]
    return jsonify(roles)

@agents_bp.route('/agents/statistics', methods=['GET'])
def get_agent_statistics():
    """Get agent statistics"""
    total_agents = Agent.query.count()
    active_agents = Agent.query.filter(Agent.status != 'idle').count()
    
    # Count by role
    role_counts = {}
    roles = db.session.query(Agent.role, db.func.count(Agent.id)).group_by(Agent.role).all()
    for role, count in roles:
        role_counts[role] = count
    
    # Count by status
    status_counts = {}
    statuses = db.session.query(Agent.status, db.func.count(Agent.id)).group_by(Agent.status).all()
    for status, count in statuses:
        status_counts[status] = count
    
    # Average energy and health
    avg_stats = db.session.query(
        db.func.avg(Agent.energy).label('avg_energy'),
        db.func.avg(Agent.health).label('avg_health')
    ).first()
    
    return jsonify({
        'total_agents': total_agents,
        'active_agents': active_agents,
        'role_distribution': role_counts,
        'status_distribution': status_counts,
        'average_energy': float(avg_stats.avg_energy) if avg_stats.avg_energy else 0,
        'average_health': float(avg_stats.avg_health) if avg_stats.avg_health else 0
    })

@agents_bp.route('/agents/bulk', methods=['POST'])
def create_bulk_agents():
    """Create multiple agents at once"""
    data = request.json
    agents_data = data.get('agents', [])
    
    created_agents = []
    for agent_data in agents_data:
        agent = Agent(
            name=agent_data['name'],
            role=agent_data['role'],
            x=agent_data.get('x', 0.0),
            y=agent_data.get('y', 0.0),
            status=agent_data.get('status', 'idle'),
            energy=agent_data.get('energy', 100.0),
            health=agent_data.get('health', 100.0),
            current_location_id=agent_data.get('current_location_id')
        )
        
        if 'schedule' in agent_data:
            agent.set_schedule(agent_data['schedule'])
        if 'preferences' in agent_data:
            agent.set_preferences(agent_data['preferences'])
        
        db.session.add(agent)
        created_agents.append(agent)
    
    db.session.commit()
    
    # Convert to dict after commit to get IDs
    result = [agent.to_dict() for agent in created_agents]
    
    return jsonify({
        'message': f'Created {len(created_agents)} agents',
        'agents': result
    }), 201

