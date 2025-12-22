import time
import math
import sys
import os
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
PLAYER_START_POS = [4, 6]   # [row, col] - centered in maze

# ADOM-style ASCII characters (darker to brighter)
SHADES = [
    ' ',   # 0: Pure darkness
    '·',   # 1: Very dim
    '.',   # 2: Dim
    ':',   # 3: Medium dim
    '░',   # 4: Light
    '▒',   # 5: Medium light
    '▓',   # 6: Bright
    '█',   # 7: Very bright
]
NUM_SHADES = len(SHADES) - 1

# --- Maze Definition (ADOM-style) ---
MAZE = [
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

# --- Core Functions ---

def clear_screen():
    """Clears the console for fresh rendering."""
    print("\033[H\033[J", end="")

def get_breathing_phase(t):
    """Returns the current breathing phase and time within that phase."""
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

def get_current_radius(phase_progress):
    """Calculate current light radius based on breathing phase."""
    # phase_progress: 0.0 to 1.0
    # Smooth transition using ease-in-out
    smoothed = 0.5 - 0.5 * math.cos(phase_progress * math.pi)
    return MIN_LIGHT_RADIUS + (MAX_LIGHT_RADIUS - MIN_LIGHT_RADIUS) * smoothed

def distance_euclidean(r1, c1, r2, c2):
    """Calculates Euclidean distance."""
    return math.sqrt((r1 - r2)**2 + (c1 - c2)**2)

def get_light_intensity(player_r, player_c, r, c, current_radius):
    """Calculates light intensity at a given position."""
    dist = distance_euclidean(player_r, player_c, r, c)
    
    if dist <= 1.0:
        # Player position and immediate vicinity
        return 1.0
    
    if dist > current_radius:
        # Beyond light radius
        return 0.0
    
    # Smooth falloff within radius
    intensity = 1.0 - (dist / current_radius)
    # Apply power curve for more dramatic falloff
    intensity = intensity ** 1.5
    
    return max(0.0, min(1.0, intensity))

def render_progress_bar(phase_time, phase_duration, width=30):
    """Renders a simple progress bar."""
    filled = int((phase_time / phase_duration) * width)
    bar = '█' * filled + '░' * (width - filled)
    return bar

def render_maze(player_pos, start_time):
    """Renders the maze with ADOM-style breathing light."""
    
    t = time.time() - start_time
    phase, phase_time, phase_duration, phase_progress = get_breathing_phase(t)
    current_radius = get_current_radius(phase_progress)
    
    player_r, player_c = player_pos
    
    # Build maze output
    output = []
    for r, row in enumerate(MAZE):
        line = ""
        for c, char in enumerate(row):
            # Calculate light intensity for this cell
            intensity = get_light_intensity(player_r, player_c, r, c, current_radius)
            
            # Map intensity to shade index
            shade_index = math.floor(intensity * NUM_SHADES)
            shade_char = SHADES[shade_index]
            
            # Determine display character
            if r == player_r and c == player_c:
                # Player character
                if phase == "INHALE":
                    display = Fore.CYAN + '@' + Fore.RESET
                elif phase == "HOLD":
                    display = Fore.YELLOW + '@' + Fore.RESET
                else:  # EXHALE
                    display = Fore.BLUE + '@' + Fore.RESET
            elif char == '#':
                # Walls - show in dim color
                if intensity > 0.1:
                    display = Fore.WHITE + shade_char + Fore.RESET
                else:
                    display = Fore.BLACK + '#' + Fore.RESET
            else:
                # Floor
                if intensity > 0.6:
                    display = Fore.LIGHTWHITE_EX + shade_char + Fore.RESET
                elif intensity > 0.3:
                    display = Fore.WHITE + shade_char + Fore.RESET
                elif intensity > 0.1:
                    display = Fore.LIGHTBLACK_EX + shade_char + Fore.RESET
                else:
                    display = Fore.BLACK + shade_char + Fore.RESET
            
            line += display
        output.append(line)
    
    # Print maze
    clear_screen()
    print("\n" + "\n".join(output))
    
    # Breathing instruction bar at bottom
    time_remaining = phase_duration - phase_time
    progress_bar = render_progress_bar(phase_time, phase_duration, 40)
    
    print("\n" + "─" * 50)
    
    # Phase indicator with color
    if phase == "INHALE":
        phase_display = Fore.CYAN + Style.BRIGHT + "INHALE" + Style.RESET_ALL
    elif phase == "HOLD":
        phase_display = Fore.YELLOW + Style.BRIGHT + "HOLD  " + Style.RESET_ALL
    else:
        phase_display = Fore.BLUE + Style.BRIGHT + "EXHALE" + Style.RESET_ALL
    
    print(f" {phase_display}  [{progress_bar}] {time_remaining:.1f}s")
    print(f" Radius: {current_radius:.1f} | Cycle: {int(t // TOTAL_CYCLE) + 1}")
    print("\n" + Fore.LIGHTBLACK_EX + " Press Ctrl+C to exit" + Fore.RESET)

def main():
    """Main game loop."""
    start_time = time.time()
    player_pos = PLAYER_START_POS
    
    print("\n" + Style.BRIGHT + "=== BREATHING MEDITATION ===" + Style.RESET_ALL)
    print("\nFind a comfortable position.")
    print("Follow the light as you breathe...\n")
    time.sleep(2)
    
    try:
        while True:
            render_maze(player_pos, start_time)
            time.sleep(0.05)  # 20 FPS for smooth animation
            
    except KeyboardInterrupt:
        clear_screen()
        print("\n" + Style.BRIGHT + "Session complete. Namaste. 🙏\n" + Style.RESET_ALL)

if __name__ == "__main__":
    main()