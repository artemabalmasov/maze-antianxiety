import time
import math
import os
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform ANSI support
init(autoreset=True)

# --- Configuration ---
BREATHING_CYCLE_TIME = 8.0  # seconds for a full light pulse (e.g., 4s inhale, 4s exhale)
MIN_LIGHT_RADIUS = 3.0      # Minimum distance where light is noticeable
MAX_LIGHT_RADIUS = 10.0     # Maximum distance for light decay
PLAYER_START_POS = [1, 1]   # [row, col]

# Grayscale characters/colors (higher index = brighter/closer)
# We use simple background colors to simulate light more clearly
SHADES = [
    Back.BLACK,         # 0: Pure Darkness
    Back.BLUE + Fore.BLACK + '░',  # 1: Very Dim Blue
    Back.BLUE + Fore.WHITE + '▒',  # 2: Dim Blue
    Back.LIGHTBLUE_EX + Fore.WHITE + '▓',  # 3: Medium Blue
    Back.CYAN + Fore.WHITE + '█'    # 4: Bright Cyan (Torch focus)
]
NUM_SHADES = len(SHADES) - 1

# --- Maze Definition ---
MAZE = [
    "#############",
    "#P. . . . . #",
    "#.###.###.#.#",
    "#...#.#...#.#",
    "###.#.#.###.#",
    "#...#.#.#...#",
    "#.#####.#####",
    "#. . . . . .#",
    "#############",
]

# --- Core Functions ---

def clear_screen():
    """Clears the console for fresh rendering."""
    # ANSI escape code to clear screen and move cursor to (0, 0)
    print("\033[H\033[J", end="") 

def breathing_factor(t):
    """Generates a smooth, rhythmic factor (0.0 to 1.0) based on time."""
    # Use sine wave to create a smooth, calming cycle
    # (sin(x) + 1) / 2 converts -1 to 1 range to 0 to 1 range
    return (math.sin(t * (2 * math.pi / BREATHING_CYCLE_TIME)) + 1) / 2

def distance_factor(r1, c1, r2, c2):
    """Calculates the light intensity based on distance (Manhattan distance)."""
    dist = abs(r1 - r2) + abs(c1 - c2)
    
    if dist < MIN_LIGHT_RADIUS:
        # Full intensity near the player
        return 1.0
    
    if dist > MAX_LIGHT_RADIUS:
        # No light beyond max radius
        return 0.0
        
    # Linear decay between min and max radius
    decay_range = MAX_LIGHT_RADIUS - MIN_LIGHT_RADIUS
    current_decay = dist - MIN_LIGHT_RADIUS
    
    # Factor goes from 1.0 down to 0.0
    return 1.0 - (current_decay / decay_range)


def render_maze(player_pos, start_time):
    """Renders the maze with rhythmic brightness."""
    
    # 1. Calculate time-based breathing factor
    t = time.time() - start_time
    breathing = breathing_factor(t)

    output = ""
    player_r, player_c = player_pos
    
    for r, row in enumerate(MAZE):
        for c, char in enumerate(row):
            
            # 2. Calculate distance factor
            distance = distance_factor(player_r, player_c, r, c)
            
            # 3. Calculate final brightness (0.0 to 1.0)
            final_brightness = distance * breathing 
            
            # Clamp the value (shouldn't be necessary but good practice)
            final_brightness = max(0.0, min(1.0, final_brightness))

            # 4. Map brightness to a shade/color index
            shade_index = math.floor(final_brightness * NUM_SHADES)
            
            # Get the color/char mapping
            shade = SHADES[shade_index]
            
            # Determine the character to display
            display_char = char
            if char == '#': # Wall symbol
                display_char = '█'
            elif char == ' ': # Floor symbol
                display_char = '.'
            
            # Display the player as a special character (always brightest)
            if r == player_r and c == player_c:
                 cell_output = Back.YELLOW + Fore.BLACK + 'P'
            else:
                 cell_output = f"{shade}{display_char}"

            output += cell_output
        output += Style.RESET_ALL + "\n" # Reset style and newline

    print(f"Breathing Factor: {breathing:.2f} | Time: {t:.1f}s")
    print("-" * len(MAZE[0]))
    print(output)
    print("Use WASD to move (or Ctrl+C to stop)")


def main():
    start_time = time.time()
    player_pos = PLAYER_START_POS
    
    try:
        while True:
            clear_screen()
            render_maze(player_pos, start_time)
            
            # Basic non-blocking input (requires specific terminal setup 
            # or a library like 'readchar'. For simplicity, we use time.sleep 
            # and let the user interrupt with Ctrl+C for now)
            # 
            # For a true game, you would use a dedicated input library or Pygame.
            
            time.sleep(0.1) # Update display 10 times per second for smooth flicker
            
    except KeyboardInterrupt:
        print("\n\nCalmSphere Lighting Test Halted.")

if __name__ == "__main__":
    main()