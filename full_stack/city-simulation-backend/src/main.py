import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from src.models.user import db
from src.routes.user import user_bp
from src.routes.simulation import simulation_bp
from src.routes.agents import agents_bp
from src.simulation.engine import SimulationEngine

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'city_simulation_secret_key_2024'

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(simulation_bp, url_prefix='/api')
app.register_blueprint(agents_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initialize simulation engine
simulation_engine = SimulationEngine(socketio)
app.simulation_engine = simulation_engine

with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_simulation')
def handle_start_simulation(data):
    app.simulation_engine.start_simulation(data)

@socketio.on('stop_simulation')
def handle_stop_simulation():
    app.simulation_engine.stop_simulation()

@socketio.on('add_agent')
def handle_add_agent(data):
    app.simulation_engine.add_agent(data)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
