import math
import random

FLOOR_CHARS = [' ', ' ', '·', '·', '·', '·', '·', '·']
WALL_CHAR = '#'

FLOOR_COLORS = [
    '#000000', '#000000', '#1a1a1a', '#333333',
    '#4d4d4d', '#666666', '#999999', '#cccccc'
]

WALL_COLORS = [
    '#000000', '#000000', '#1a1a1a', '#2d2d2d',
    '#404040', '#5a5a5a', '#7a7a7a', '#aaaaaa'
]


class Maze:
    """Manages the maze layout."""
    
    def __init__(self, layout):
        self.layout = layout
        self.height = len(layout)
        self.width = len(layout[0]) if layout else 0
    
    def get_cell(self, row, col):
        """Get cell character at position."""
        if 0 <= row < self.height and 0 <= col < len(self.layout[row]):
            return self.layout[row][col]
        return '#'
    
    @staticmethod
    def distance_euclidean(r1, c1, r2, c2):
        """Calculate Euclidean distance between two points."""
        return math.sqrt((r1 - r2)**2 + (c1 - c2)**2)
    
    def get_light_intensity(self, player_row, player_col, row, col, current_radius):
        """Calculate light intensity at a given position."""
        dist = self.distance_euclidean(player_row, player_col, row, col)
        
        if dist <= 1.0:
            return 1.0
        
        if dist > current_radius:
            return 0.0
        
        intensity = 1.0 - (dist / current_radius)
        intensity = intensity ** 1.5
        
        return max(0.0, min(1.0, intensity))
    
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
    
    def render_visible_area(self, player_row, player_col, current_radius):
        """Render only the visible area around the player."""
        visible_cells = []
        
        # Calculate bounding box
        min_row = max(0, int(player_row - current_radius - 2))
        max_row = min(self.height, int(player_row + current_radius + 3))
        min_col = max(0, int(player_col - current_radius - 2))
        max_col = min(self.width, int(player_col + current_radius + 3))
        
        for r in range(min_row, max_row):
            for c in range(min_col, max_col):
                intensity = self.get_light_intensity(player_row, player_col, r, c, current_radius)
                
                if intensity > 0:
                    color_index = min(7, int(intensity * 7))
                    cell = self.get_cell(r, c)
                    
                    if r == player_row and c == player_col:
                        cell_type = 'player'
                        char = '@'
                        color = None  # Will be calculated on frontend
                    elif cell == '#':
                        cell_type = 'wall'
                        char = '#'
                        color = WALL_COLORS[color_index]
                    else:
                        cell_type = 'floor'
                        char = FLOOR_CHARS[color_index]
                        color = FLOOR_COLORS[color_index]
                    
                    visible_cells.append({
                        'row': r,
                        'col': c,
                        'type': cell_type,
                        'char': char,
                        'color': color,
                        'intensity': intensity
                    })
        
        return visible_cells
    