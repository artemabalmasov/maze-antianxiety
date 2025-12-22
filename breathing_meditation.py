import time
import math
import sys
import os
import tty
import termios
import select
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform ANSI support
init(autoreset=True)

# --- Configuration ---
INHALE_TIME = 4.0      # seconds
HOLD_TIME = 2.0        # seconds
EXHALE_TIME = 6.0      # seconds
TOTAL_CYCLE = INHALE_TIME + HOLD_TIME + EXHALE_TIME

MIN_LIGHT_RADIUS = 2.0      # Minimum radius when exhaled
MAX_LIGHT_RADIUS = 12.0     # Maximum radius when inhaled

# ADOM-style brightness levels using actual color intensity
# Each shade is [color_code, character]
SHADES = [
    (Fore.BLACK, ' '),              # 0: Pure darkness
    (Fore.BLACK, '·'),              # 1: Very dim
    (Fore.LIGHTBLACK_EX, '·'),      # 2: Dim
    (Fore.LIGHTBLACK_EX, '.'),      # 3: Medium dim
    (Fore.WHITE, '·'),              # 4: Light
    (Fore.WHITE, '.'),              # 5: Medium light
    (Fore.LIGHTWHITE_EX, '·'),      # 6: Bright
    (Fore.LIGHTWHITE_EX, '.'),      # 7: Very bright
]
NUM_SHADES = len(SHADES) - 1

# Wall and floor characters with brightness
WALL_SHADES = [
    (Fore.BLACK, '#'),
    (Fore.BLACK, '#'),
    (Fore.LIGHTBLACK_EX, '#'),
    (Fore.LIGHTBLACK_EX, '#'),
    (Fore.WHITE, '#'),
    (Fore.WHITE, '#'),
    (Fore.LIGHTWHITE_EX, '#'),
    (Fore.LIGHTWHITE_EX, '#'),
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
        elif cycle_time < INHALE_TIME + HOLD_TIME:
            phase = "HOLD"
            phase_time = cycle_time - INHALE_TIME
            phase_duration = HOLD_TIME
            phase_progress = 1.0  # Stay at maximum
        else:
            phase = "EXHALE"
            phase_time = cycle_time - INHALE_TIME - HOLD_TIME
            phase_duration = EXHALE_TIME
            phase_progress = 1.0 - (phase_time / phase_duration)
        
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
    """Manages the maze layout and rendering."""
    
    def __init__(self, layout):
        # DO NOT strip rows — it can change widths
        self.height = len(layout)
        self.width = max(len(row) for row in layout)

        # Pad every row to full width
        self.layout = [row.ljust(self.width, '#') for row in layout]
    
    def get_cell(self, row, col):
        """Get cell character at position."""
        if 0 <= row < self.height:
            if 0 <= col < len(self.layout[row]):
                return self.layout[row][col]
        return '#'
    
    def is_walkable(self, row, col):
        """Check if position is walkable."""
        return self.get_cell(row, col) != '#'
    
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

class Renderer2:
    """Handles all screen rendering."""
    
    @staticmethod
    def clear_screen():
        """Move cursor to home and clear screen."""
        # \033[H moves cursor to top-left, \033[J clears from cursor to end of screen
        print("\033[H\033[J", end="", flush=True)

    @staticmethod
    def render_progress_bar(phase_time, phase_duration, width=40):
        """Render a progress bar."""
        progress = max(0, min(1, phase_time / phase_duration))
        filled = int(progress * width)
        bar = '█' * filled + '░' * (width - filled)
        return bar
    
    def render_maze(self, maze, player, breathing_state):
        """Render the complete maze with lighting."""
        phase, phase_time, phase_duration, _ = breathing_state.get_breathing_phase()
        current_radius = breathing_state.get_current_radius()
        
        # Build maze output into a buffer
        # We start by moving the cursor to the top-left corner (0,0)
        output_buffer = "\033[H" 
        
        for r in range(maze.height):
            line = ""
            for c in range(maze.width):
                intensity = maze.get_light_intensity(
                    player.row, player.col, r, c, current_radius
                )
                shade_index = math.floor(intensity * NUM_SHADES)
                
                if r == player.row and c == player.col:
                    if phase == "INHALE":
                        display = Fore.CYAN + Style.BRIGHT + '@' + Style.RESET_ALL
                    elif phase == "HOLD":
                        display = Fore.YELLOW + Style.BRIGHT + '@' + Style.RESET_ALL
                    else:
                        display = Fore.BLUE + Style.BRIGHT + '@' + Style.RESET_ALL
                elif maze.get_cell(r, c) == '#':
                    color, char = WALL_SHADES[shade_index]
                    display = color + char + Fore.RESET
                else:
                    color, char = SHADES[shade_index]
                    display = color + char + Fore.RESET
                
                line += display
            
            # \033[K clears the line to the right to prevent ghost characters
            output_buffer += line + "\033[K\n"
        
        # Add the status bar to the buffer
        output_buffer += self._get_status_bar_string(breathing_state, current_radius)
        
        # Print the entire frame at once
        sys.stdout.write(output_buffer)
        sys.stdout.flush()
    
    def _get_status_bar_string(self, breathing_state, current_radius):
        """Build the status bar string."""
        phase, phase_time, phase_duration, _ = breathing_state.get_breathing_phase()
        time_remaining = max(0, phase_duration - phase_time)
        progress_bar = self.render_progress_bar(phase_time, phase_duration, 40)
        
        # Formatting the phase text
        if phase == "INHALE":
            phase_display = Fore.CYAN + Style.BRIGHT + "INHALE" + Style.RESET_ALL
        elif phase == "HOLD":
            phase_display = Fore.YELLOW + Style.BRIGHT + "HOLD  " + Style.RESET_ALL
        else:
            phase_display = Fore.BLUE + Style.BRIGHT + "EXHALE" + Style.RESET_ALL
            
        status = (
            "\n" + "─" * 50 + "\n" +
            f" {phase_display}  [{progress_bar}] {time_remaining:.1f}s\033[K\n" +
            f" Radius: {current_radius:.1f} | Cycle: {breathing_state.get_cycle_number()}\033[K\n" +
            Fore.LIGHTBLACK_EX + " WASD to move | Ctrl+C to exit" + Fore.RESET + "\033[K\n"
        )
        return status
class Renderer:
    """Handles all screen rendering."""
    
    @staticmethod
    def clear_screen():
        """Clear the console."""
        print("\033[2J\033[H", end="", flush=True)
    
    @staticmethod
    def render_progress_bar(phase_time, phase_duration, width=40):
        """Render a progress bar."""
        filled = int((phase_time / phase_duration) * width)
        bar = '█' * filled + '░' * (width - filled)
        return bar
    
    def render_maze(self, maze, player, breathing_state):
        """Render the complete maze with lighting."""
        phase, phase_time, phase_duration, _ = breathing_state.get_breathing_phase()
        current_radius = breathing_state.get_current_radius()
        
        # Build maze output
        output = []
        for r in range(maze.height):
            line = ""
            for c in range(maze.width):
                # Calculate light intensity for this cell
                intensity = maze.get_light_intensity(
                    player.row, player.col, r, c, current_radius
                )
                
                # Map intensity to shade index
                shade_index = math.floor(intensity * NUM_SHADES)
                
                # Render cell
                if r == player.row and c == player.col:
                    # Player character
                    if phase == "INHALE":
                        display = Fore.CYAN + Style.BRIGHT + '@' + Style.RESET_ALL
                    elif phase == "HOLD":
                        display = Fore.YELLOW + Style.BRIGHT + '@' + Style.RESET_ALL
                    else:  # EXHALE
                        display = Fore.BLUE + Style.BRIGHT + '@' + Style.RESET_ALL
                elif maze.get_cell(r, c) == '#':
                    # Wall
                    color, char = WALL_SHADES[shade_index]
                    display = color + char + Fore.RESET
                else:
                    # Floor
                    color, char = SHADES[shade_index]
                    display = color + char + Fore.RESET
                
                line += display
            output.append(line)
        
        # Clear and print maze
        self.clear_screen()
        for line in output:
            print("\033[K" + line)
            # print(line)
        
        # Render breathing instruction bar
        self._render_status_bar(breathing_state, current_radius)
    
    def _render_status_bar(self, breathing_state, current_radius):
        """Render the status bar at the bottom."""
        phase, phase_time, phase_duration, _ = breathing_state.get_breathing_phase()
        time_remaining = phase_duration - phase_time
        progress_bar = self.render_progress_bar(phase_time, phase_duration, 40)
        
        print("\n" + "─" * 50)
        
        # Phase indicator with color
        if phase == "INHALE":
            phase_display = Fore.CYAN + Style.BRIGHT + "INHALE" + Style.RESET_ALL
        elif phase == "HOLD":
            phase_display = Fore.YELLOW + Style.BRIGHT + "HOLD  " + Style.RESET_ALL
        else:
            phase_display = Fore.BLUE + Style.BRIGHT + "EXHALE" + Style.RESET_ALL
        
        print(f" {phase_display}  [{progress_bar}] {time_remaining:.1f}s")
        print(f" Radius: {current_radius:.1f} | Cycle: {breathing_state.get_cycle_number()}")
        print("\n" + Fore.LIGHTBLACK_EX + " WASD to move | Ctrl+C to exit" + Fore.RESET)


class InputHandler:
    """Handles keyboard input in a non-blocking way."""
    
    def __init__(self):
        self.fd = None
        self.old_settings = None
        self.is_tty = sys.stdin.isatty()
        if self.is_tty:
            self.fd = sys.stdin.fileno()
    
    def __enter__(self):
        """Set up terminal for raw input."""
        if self.is_tty:
            try:
                self.old_settings = termios.tcgetattr(self.fd)
                tty.setraw(self.fd)
            except (termios.error, AttributeError):
                self.is_tty = False
        return self
    
    def __exit__(self, *args):
        """Restore terminal settings."""
        if self.old_settings and self.is_tty:
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old_settings)
            except (termios.error, AttributeError):
                pass
    
    def get_key(self, timeout=0.0):
        """Get a key press if available (non-blocking)."""
        if not self.is_tty:
            return None
        
        try:
            # Check if input is available
            rlist, _, _ = select.select([sys.stdin], [], [], timeout)
            if rlist:
                key = sys.stdin.read(1)
                return key
        except (OSError, ValueError):
            pass
        return None


class Game:
    """Main game controller."""
    
    def __init__(self):
        # Define maze
        maze_layout = [
            "#####################",
            "#...................#",
            "#.#####.#####.#####.#",
            "#.#...#.#...#.#...#.#",
            "#.#.#.#.#.#.#.#.#.#.#",
            "#...#...#.#...#.#...#",
            "#####.#####.#####.###",
            "#.....#.....#.......#",
            "#.#####.#####.#####.#",
            "#...................#",
            "#####################",
        ]
        
        self.maze = Maze(maze_layout)
        self.player = Player(5, 10)  # Start in center-ish area
        self.breathing_state = BreathingState()
        self.renderer = Renderer()
        self.running = True
    
    def handle_input(self, key):
        """Process keyboard input."""
        if key:
            key = key.lower()
            if key == 'w':
                self.player.move(-1, 0, self.maze.layout)
            elif key == 's':
                self.player.move(1, 0, self.maze.layout)
            elif key == 'a':
                self.player.move(0, -1, self.maze.layout)
            elif key == 'd':
                self.player.move(0, 1, self.maze.layout)
            elif key == 'q' or key == '\x03':  # q or Ctrl+C
                self.running = False
    
    def run(self):
        """Main game loop."""
        print("\n" + Style.BRIGHT + "=== BREATHING MEDITATION ===" + Style.RESET_ALL)
        print("\nFind a comfortable position.")
        print("Follow the light as you breathe...")
        print("Use WASD to explore the space.\n")
        time.sleep(2)
        
        try:
            with InputHandler() as input_handler:
                while self.running:
                    # Render
                    self.renderer.render_maze(self.maze, self.player, self.breathing_state)
                    
                    # Handle input (non-blocking with short timeout)
                    key = input_handler.get_key(timeout=0.05)
                    self.handle_input(key)
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.renderer.clear_screen()
            print("\n" + Style.BRIGHT + "Session complete. Namaste. 🙏\n" + Style.RESET_ALL)


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
