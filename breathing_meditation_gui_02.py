import time
import math
import tkinter as tk
from tkinter import font as tkfont

# --- Configuration ---
INHALE_TIME = 4.0      # seconds
HOLD_AFTER_INHALE = 2.0        # seconds
EXHALE_TIME = 6.0      # seconds
HOLD_AFTER_EXHALE = 2.0        # seconds (configurable)
TOTAL_CYCLE = INHALE_TIME + HOLD_AFTER_INHALE + EXHALE_TIME + HOLD_AFTER_EXHALE

MIN_LIGHT_RADIUS = 2.0      # Minimum radius when exhaled
MAX_LIGHT_RADIUS = 12.0     # Maximum radius when inhaled

CELL_SIZE = 10  # Pixel size of each cell (smaller for 100x100 maze)
FPS = 30  # Frames per second

# ADOM-style characters (darker to brighter)
# FLOOR_CHARS = [' ', ' ', '·', '·', ':', ':', '░', '▒']
FLOOR_CHARS = [' ', ' ', '·', '·', '·', '·', '·', '·']
WALL_CHAR = '#'

# Color gradients (RGB) from absolute black to bright
# Index 0 and 1 are completely invisible (black on black)
FLOOR_COLORS = [
    '#000000',  # Absolute black - invisible
    '#000000',  # Absolute black - invisible
    '#1a1a1a',  # Very faint
    '#333333',  # Dark gray
    '#4d4d4d',  # Medium-dark gray
    '#666666',  # Medium gray
    '#999999',  # Light gray
    '#cccccc',  # Very light gray
]

WALL_COLORS = [
    '#000000',  # Absolute black - invisible
    '#000000',  # Absolute black - invisible
    '#1a1a1a',  # Very faint
    '#2d2d2d',  # Dark gray
    '#404040',  # Medium-dark gray
    '#5a5a5a',  # Medium gray
    '#7a7a7a',  # Light gray
    '#aaaaaa',  # Very light gray
]


class BreathingState:
    """Manages the breathing cycle and light radius."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        """Get time elapsed since start."""
        return time.time() - self.start_time
    
    def get_breathing_phase(self):
        """Returns the current breathing phase and progress."""
        t = self.get_elapsed_time()
        cycle_time = t % TOTAL_CYCLE
        
        if cycle_time < INHALE_TIME:
            phase = "INHALE"
            phase_time = cycle_time
            phase_duration = INHALE_TIME
            phase_progress = phase_time / phase_duration
        elif cycle_time < INHALE_TIME + HOLD_AFTER_INHALE:
            phase = "HOLD"
            phase_time = cycle_time - INHALE_TIME
            phase_duration = HOLD_AFTER_INHALE
            phase_progress = 1.0  # Stay at maximum
        elif cycle_time < INHALE_TIME + HOLD_AFTER_INHALE + EXHALE_TIME:
            phase = "EXHALE"
            phase_time = cycle_time - INHALE_TIME - HOLD_AFTER_INHALE
            phase_duration = EXHALE_TIME
            phase_progress = 1.0 - (phase_time / phase_duration)
        else:
            phase = "HOLD"
            phase_time = cycle_time - INHALE_TIME - HOLD_AFTER_INHALE - EXHALE_TIME
            phase_duration = HOLD_AFTER_EXHALE
            phase_progress = 0.0  # Stay at minimum
        
        return phase, phase_time, phase_duration, phase_progress
    
    def get_current_radius(self):
        """Calculate current light radius based on breathing phase."""
        _, _, _, phase_progress = self.get_breathing_phase()
        # Smooth transition using ease-in-out
        smoothed = 0.5 - 0.5 * math.cos(phase_progress * math.pi)
        return MIN_LIGHT_RADIUS + (MAX_LIGHT_RADIUS - MIN_LIGHT_RADIUS) * smoothed
    
    def get_cycle_number(self):
        """Get current cycle number."""
        return int(self.get_elapsed_time() // TOTAL_CYCLE) + 1


class Player:
    """Manages player position and movement."""
    
    def __init__(self, start_row, start_col):
        self.row = start_row
        self.col = start_col
    
    def move(self, dr, dc, maze):
        """Attempt to move player in given direction."""
        new_row = self.row + dr
        new_col = self.col + dc
        
        # Check bounds
        if 0 <= new_row < len(maze) and 0 <= new_col < len(maze[0]):
            # Check if target is walkable (not a wall)
            if maze[new_row][new_col] != '#':
                self.row = new_row
                self.col = new_col
                return True
        return False


class Maze:
    """Manages the maze layout."""
    
    def __init__(self, layout):
        self.layout = [row.strip() for row in layout]
        self.height = len(self.layout)
        self.width = max(len(row) for row in self.layout) if self.layout else 0
    
    def get_cell(self, row, col):
        """Get cell character at position."""
        if 0 <= row < self.height:
            if 0 <= col < len(self.layout[row]):
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
        
        # Smooth falloff within radius
        intensity = 1.0 - (dist / current_radius)
        intensity = intensity ** 1.5
        
        return max(0.0, min(1.0, intensity))


class BreathingMeditationGUI:
    """Main GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Breathing Meditation")
        
        # Generate 100x100 maze
        self.maze = Maze(self.generate_large_maze(100, 100))
        self.player = Player(50, 50)  # Start in center
        self.breathing_state = BreathingState()
        
        # Calculate window size
        self.width = self.maze.width * CELL_SIZE
        self.height = self.maze.height * CELL_SIZE + 100  # Extra space for status
        
        # Create canvas
        self.canvas = tk.Canvas(
            root, 
            width=self.width, 
            height=self.height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Setup font
        self.cell_font = tkfont.Font(family="Courier", size=int(CELL_SIZE * 0.6), weight="bold")
        self.status_font = tkfont.Font(family="Arial", size=14, weight="bold")
        self.info_font = tkfont.Font(family="Arial", size=10)
        
        # Bind keys
        self.root.bind('<w>', lambda e: self.player.move(-1, 0, self.maze.layout))
        self.root.bind('<s>', lambda e: self.player.move(1, 0, self.maze.layout))
        self.root.bind('<a>', lambda e: self.player.move(0, -1, self.maze.layout))
        self.root.bind('<d>', lambda e: self.player.move(0, 1, self.maze.layout))
        self.root.bind('<W>', lambda e: self.player.move(-1, 0, self.maze.layout))
        self.root.bind('<S>', lambda e: self.player.move(1, 0, self.maze.layout))
        self.root.bind('<A>', lambda e: self.player.move(0, -1, self.maze.layout))
        self.root.bind('<D>', lambda e: self.player.move(0, 1, self.maze.layout))
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Start animation loop
        self.animate()
    
    def get_player_color(self, phase):
        """Get player color based on breathing phase."""
        if phase == "INHALE":
            return '#00FFFF'  # Cyan
        elif phase == "HOLD":
            return '#FFFF00'  # Yellow
        else:  # EXHALE
            return '#0088FF'  # Blue
    
    def generate_large_maze(self, width, height):
        """Generate a large maze using recursive backtracking."""
        import random
        
        # Create a grid filled with walls
        maze = [['#' for _ in range(width)] for _ in range(height)]
        
        # Start from center
        start_x, start_y = width // 2, height // 2
        
        # Stack for DFS
        stack = [(start_x, start_y)]
        visited = set()
        visited.add((start_x, start_y))
        maze[start_y][start_x] = '.'
        
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        
        while stack:
            x, y = stack[-1]
            
            # Find unvisited neighbors
            neighbors = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 1 <= nx < width - 1 and 1 <= ny < height - 1:
                    if (nx, ny) not in visited:
                        neighbors.append((nx, ny, dx, dy))
            
            if neighbors:
                # Choose random neighbor
                nx, ny, dx, dy = random.choice(neighbors)
                
                # Carve path
                maze[y + dy // 2][x + dx // 2] = '.'
                maze[ny][nx] = '.'
                
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Add some open rooms for variety
        for _ in range(20):
            room_x = random.randint(5, width - 10)
            room_y = random.randint(5, height - 10)
            room_w = random.randint(3, 8)
            room_h = random.randint(3, 8)
            
            for ry in range(room_y, min(room_y + room_h, height - 1)):
                for rx in range(room_x, min(room_x + room_w, width - 1)):
                    if 1 <= rx < width - 1 and 1 <= ry < height - 1:
                        maze[ry][rx] = '.'
        
        # Convert to strings
        return [''.join(row) for row in maze]
    
    def render_maze(self):
        """Render the maze with lighting."""
        self.canvas.delete("all")
        
        phase, phase_time, phase_duration, _ = self.breathing_state.get_breathing_phase()
        current_radius = self.breathing_state.get_current_radius()
        
        # Render each cell
        for r in range(self.maze.height):
            for c in range(self.maze.width):
                # Calculate position
                x = c * CELL_SIZE
                y = r * CELL_SIZE
                
                # Calculate light intensity
                intensity = self.maze.get_light_intensity(
                    self.player.row, self.player.col, r, c, current_radius
                )
                
                # Map intensity to color index
                color_index = min(7, int(intensity * 7))
                
                # Get cell type
                cell = self.maze.get_cell(r, c)
                
                # Render cell
                if r == self.player.row and c == self.player.col:
                    # Player - colored @ character on black background
                    color = self.get_player_color(phase)
                    self.canvas.create_rectangle(
                        x, y, x + CELL_SIZE, y + CELL_SIZE,
                        fill='black', outline=''
                    )
                    self.canvas.create_text(
                        x + CELL_SIZE // 2, y + CELL_SIZE // 2,
                        text='@', font=self.cell_font, fill=color
                    )
                elif cell == '#':
                    # Wall - always render # character
                    color = WALL_COLORS[color_index]
                    self.canvas.create_rectangle(
                        x, y, x + CELL_SIZE, y + CELL_SIZE,
                        fill='black', outline=''
                    )
                    # Always show # character for walls
                    self.canvas.create_text(
                        x + CELL_SIZE // 2, y + CELL_SIZE // 2,
                        text='#', font=self.cell_font, fill=color
                    )
                else:
                    # Floor - show pseudo-ASCII based on light level
                    color = FLOOR_COLORS[color_index]
                    char = FLOOR_CHARS[color_index]
                    self.canvas.create_rectangle(
                        x, y, x + CELL_SIZE, y + CELL_SIZE,
                        fill='black', outline=''
                    )
                    # Only show character if there's some light (not completely dark)
                    if char != ' ':
                        self.canvas.create_text(
                            x + CELL_SIZE // 2, y + CELL_SIZE // 2,
                            text=char, font=self.cell_font, fill=color
                        )
        
        # Render status bar
        self.render_status_bar(phase, phase_time, phase_duration, current_radius)
    
    def render_status_bar(self, phase, phase_time, phase_duration, current_radius):
        """Render the status bar at the bottom."""
        status_y = self.maze.height * CELL_SIZE + 10
        
        # Phase name with color
        phase_colors = {
            "INHALE": "#00FFFF",
            "HOLD": "#FFFF00",
            "EXHALE": "#0088FF"
        }
        
        self.canvas.create_text(
            self.width // 2, status_y,
            text=phase, font=self.status_font,
            fill=phase_colors[phase]
        )
        
        # Progress bar
        bar_y = status_y + 25
        bar_width = self.width - 40
        bar_height = 20
        bar_x = 20
        
        # Background
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
            fill='#333333', outline='#666666'
        )
        
        # Progress
        progress = phase_time / phase_duration
        fill_width = int(bar_width * progress)
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + fill_width, bar_y + bar_height,
            fill=phase_colors[phase], outline=''
        )
        
        # Time remaining
        time_remaining = phase_duration - phase_time
        self.canvas.create_text(
            self.width // 2, bar_y + bar_height + 15,
            text=f"{time_remaining:.1f}s remaining",
            font=self.info_font, fill='white'
        )
        
        # Additional info
        info_y = bar_y + bar_height + 35
        cycle_num = self.breathing_state.get_cycle_number()
        self.canvas.create_text(
            self.width // 2, info_y,
            text=f"Radius: {current_radius:.1f} | Cycle: {cycle_num}",
            font=self.info_font, fill='#999999'
        )
        
        # Instructions
        self.canvas.create_text(
            self.width // 2, info_y + 20,
            text="WASD to move | ESC to exit",
            font=self.info_font, fill='#666666'
        )
    
    def animate(self):
        """Animation loop."""
        self.render_maze()
        self.root.after(int(1000 / FPS), self.animate)


def main():
    root = tk.Tk()
    app = BreathingMeditationGUI(root)
    
    # Center window
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - app.width) // 2
    y = (screen_height - app.height) // 2
    root.geometry(f"{app.width}x{app.height}+{x}+{y}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
