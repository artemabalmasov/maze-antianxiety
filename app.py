from flask import Flask, jsonify, send_from_directory
import random
import os

app = Flask(__name__, static_folder='static')


class Maze:
    """Manages maze generation only."""
    
    @staticmethod
    def generate(width, height):
        """Generate a maze using recursive backtracking."""
        maze = [['#' for _ in range(width)] for _ in range(height)]
        
        start_x, start_y = width // 2, height // 2
        
        stack = [(start_x, start_y)]
        visited = set()
        visited.add((start_x, start_y))
        maze[start_y][start_x] = '.'
        
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        
        while stack:
            x, y = stack[-1]
            
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < width - 1 and 1 <= ny < height - 1:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                maze[y + dy // 2][x + dx // 2] = '.'
                maze[ny][nx] = '.'
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Add some rooms
        for _ in range(20):
            room_x = random.randint(5, width - 10)
            room_y = random.randint(5, height - 10)
            room_w = random.randint(3, 8)
            room_h = random.randint(3, 8)
            
            for ry in range(room_y, min(room_y + room_h, height - 1)):
                for rx in range(room_x, min(room_x + room_w, width - 1)):
                    if 1 <= rx < width - 1 and 1 <= ry < height - 1:
                        maze[ry][rx] = '.'
        
        return [''.join(row) for row in maze]


@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


@app.route('/api/maze/generate', methods=['POST'])
def generate_maze():
    """Generate a new maze."""
    maze_layout = Maze.generate(100, 100)
    return jsonify({
        'maze': maze_layout,
        'width': 100,
        'height': 100
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Breathing Meditation Server'
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)