from flask import Flask, jsonify, request, send_from_directory
import time
import random
import os
from app_config import CONFIG
from breathing_state import BreathingState
from maze import Maze
from player_class import Player

app = Flask(__name__, static_folder='static')

class GameSession:
    """Manages a complete game session."""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.maze = Maze(Maze.generate(CONFIG['MAZE_SIZE'], CONFIG['MAZE_SIZE']))
        self.player = Player(50, 50)
        self.breathing_state = BreathingState(session_id)
        self.created_at = time.time()
    
    def get_state(self):
        """Get complete game state."""
        breathing_data = self.breathing_state.to_dict()
        visible_cells = self.maze.render_visible_area(
            self.player.row,
            self.player.col,
            breathing_data['current_radius']
        )
        
        return {
            'session_id': self.session_id,
            'player': self.player.to_dict(),
            'breathing': breathing_data,
            'visible_cells': visible_cells,
            'maze_size': {
                'width': self.maze.width,
                'height': self.maze.height
            }
        }
    
    def handle_move(self, direction):
        """Handle player movement."""
        success = self.player.move(direction, self.maze)
        return success


# Store active sessions
sessions = {}

# Session timeout (30 minutes)
SESSION_TIMEOUT = 1800


def cleanup_old_sessions():
    """Remove sessions older than timeout."""
    current_time = time.time()
    expired = [sid for sid, session in sessions.items() 
               if current_time - session.created_at > SESSION_TIMEOUT]
    for sid in expired:
        del sessions[sid]


@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


@app.route('/api/session/create', methods=['POST'])
def create_session():
    """Create a new game session."""
    cleanup_old_sessions()
    
    session_id = f"session_{int(time.time() * 1000)}_{random.randint(1000, 9999)}"
    sessions[session_id] = GameSession(session_id)
    
    return jsonify({
        'session_id': session_id,
        'config': CONFIG
    })


@app.route('/api/session/<session_id>/state', methods=['GET'])
def get_state(session_id):
    """Get current game state."""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    return jsonify(session.get_state())


@app.route('/api/session/<session_id>/move', methods=['POST'])
def move_player(session_id):
    """Move the player."""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    data = request.json
    direction = data.get('direction')
    
    if direction not in ['up', 'down', 'left', 'right']:
        return jsonify({'error': 'Invalid direction'}), 400
    
    session = sessions[session_id]
    success = session.handle_move(direction)
    
    return jsonify({
        'success': success,
        'player': session.player.to_dict()
    })


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get game configuration."""
    return jsonify(CONFIG)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'active_sessions': len(sessions),
        'timestamp': time.time()
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
