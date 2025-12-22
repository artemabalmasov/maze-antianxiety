import tkinter as tk
from tkinter import ttk
import time
import math

# --- Configuration ---
WIDTH = 600
HEIGHT = 400
BACKGROUND_COLOR = "#22223b" # Deep blue/purple for calm
CIRCLE_COLOR = "#a9d6e5"     # Light blue/cyan for peacefulness

# --- Breathing Parameters (in milliseconds for Tkinter timing) ---
INHALE_TIME = 4000  # 4 seconds
HOLD_IN_TIME = 2000 # 2 seconds
EXHALE_TIME = 6000  # 6 seconds
PAUSE_TIME = 2000   # 2 seconds
TOTAL_CYCLE_TIME = INHALE_TIME + HOLD_IN_TIME + EXHALE_TIME + PAUSE_TIME

MIN_RADIUS = 50
MAX_RADIUS = 150
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2

class BreathingCircleApp:
    def __init__(self, master):
        self.master = master
        master.title("CalmSphere Breathing Aid")
        master.geometry(f"{WIDTH}x{HEIGHT}")
        master.configure(bg=BACKGROUND_COLOR)
        
        # Canvas for drawing the circle
        self.canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT - 50, bg=BACKGROUND_COLOR, highlightthickness=0)
        self.canvas.pack(pady=(20, 0))
        
        # Text label for instruction
        self.instruction_label = ttk.Label(
            master, 
            text="Press START to begin", 
            font=("Helvetica", 18, "bold"), 
            background=BACKGROUND_COLOR, 
            foreground="white"
        )
        self.instruction_label.pack(pady=10)
        
        # Start button
        self.start_button = ttk.Button(master, text="START", command=self.start_breathing_loop)
        self.start_button.pack(pady=10)
        
        # Initial circle (using Tkinter's create_oval: x1, y1, x2, y2)
        r = MIN_RADIUS
        self.circle = self.canvas.create_oval(
            CENTER_X - r, CENTER_Y - r, 
            CENTER_X + r, CENTER_Y + r, 
            fill=CIRCLE_COLOR, outline=""
        )
        
        # State variables
        self.is_running = False
        self.start_time = 0
        self.current_job = None

    def start_breathing_loop(self):
        """Starts the breathing animation loop."""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_button.config(text="STOP", command=self.stop_breathing_loop)
        self.start_time = time.time() * 1000  # Start time in ms
        self.update_circle()

    def stop_breathing_loop(self):
        """Stops the breathing animation loop."""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.current_job:
            self.master.after_cancel(self.current_job)
        
        # Reset UI
        self.start_button.config(text="START", command=self.start_breathing_loop)
        self.instruction_label.config(text="Press START to begin")

    def update_circle(self):
        """Calculates the radius, updates the circle, and shows the countdown."""
        if not self.is_running:
            return

        # Calculate position within the cycle (0 to TOTAL_CYCLE_TIME)
        current_time_ms = time.time() * 1000
        elapsed = current_time_ms - self.start_time
        cycle_position = elapsed % TOTAL_CYCLE_TIME
        
        # Variables for the current phase
        radius = MIN_RADIUS
        instruction_text = ""
        
        # --- PHASE 1: INHALE --- (0ms to 4000ms)
        if 0 <= cycle_position < INHALE_TIME:
            phase_time = cycle_position
            ratio = phase_time / INHALE_TIME
            radius = MIN_RADIUS + (MAX_RADIUS - MIN_RADIUS) * ratio
            
            # Countdown Logic
            remaining_ms = INHALE_TIME - phase_time
            remaining_seconds = math.ceil(remaining_ms / 1000)
            instruction_text = f"INHALE ({remaining_seconds}s)"
            
        # --- PHASE 2: HOLD (Full Lungs) --- (4000ms to 6000ms)
        elif INHALE_TIME <= cycle_position < (INHALE_TIME + HOLD_IN_TIME):
            phase_start = INHALE_TIME
            phase_duration = HOLD_IN_TIME
            phase_time = cycle_position - phase_start
            radius = MAX_RADIUS
            
            # Countdown Logic
            remaining_ms = phase_duration - phase_time
            remaining_seconds = math.ceil(remaining_ms / 1000)
            instruction_text = f"HOLD ({remaining_seconds}s)"
            
        # --- PHASE 3: EXHALE --- (6000ms to 12000ms)
        elif (INHALE_TIME + HOLD_IN_TIME) <= cycle_position < (INHALE_TIME + HOLD_IN_TIME + EXHALE_TIME):
            phase_start = INHALE_TIME + HOLD_IN_TIME
            phase_duration = EXHALE_TIME
            phase_time = cycle_position - phase_start
            ratio = 1 - (phase_time / phase_duration) # Ratio decreases from 1 to 0
            radius = MIN_RADIUS + (MAX_RADIUS - MIN_RADIUS) * ratio
            
            # Countdown Logic
            remaining_ms = phase_duration - phase_time
            remaining_seconds = math.ceil(remaining_ms / 1000)
            instruction_text = f"EXHALE ({remaining_seconds}s)"
            
        # --- PHASE 4: PAUSE (Empty Lungs) --- (12000ms to 14000ms)
        else:
            phase_start = INHALE_TIME + HOLD_IN_TIME + EXHALE_TIME
            phase_duration = PAUSE_TIME
            phase_time = cycle_position - phase_start
            radius = MIN_RADIUS
            
            # Countdown Logic
            remaining_ms = phase_duration - phase_time
            remaining_seconds = math.ceil(remaining_ms / 1000)
            instruction_text = f"PAUSE ({remaining_seconds}s)"

        # Update Circle Size
        # Tkinter requires coordinates (x1, y1, x2, y2)
        x1 = CENTER_X - radius
        y1 = CENTER_Y - radius
        x2 = CENTER_X + radius
        y2 = CENTER_Y + radius
        self.canvas.coords(self.circle, x1, y1, x2, y2)
        
        # Update Instruction Text
        self.instruction_label.config(text=instruction_text)
        
        # Schedule the next update to run very quickly for a smooth animation
        self.current_job = self.master.after(10, self.update_circle)

# --- Start the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BreathingCircleApp(root)
    root.mainloop()