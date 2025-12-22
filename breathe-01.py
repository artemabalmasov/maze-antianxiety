import time

import math

TOTAL_CYCLE_TIME = 14
MIN_RADIUS = 50
MAX_RADIUS = 200


def main():
    calculate_circle_radius()

def calculate_circle_radius():

    start_time = time.time()

    while True:
        elapsed_time = time.time()-start_time
        cycle_position = elapsed_time % TOTAL_CYCLE_TIME
        if 0 <= cycle_position <= 4:
            phase_duration = 4
            ratio = cycle_position/phase_duration
            radius = MIN_RADIUS+(MAX_RADIUS-MIN_RADIUS)*ratio
            (f"**INHALE**: {int(radius)}")
        elif 4 <= cycle_position < 6:
            radius = MAX_RADIUS
            print(f"**HOLD:** Radius: {int(radius)}")
            
        # --- PHASE 3: EXHALE (6s to 12s) ---
        elif 6 <= cycle_position < 12:
            # Linear decrease from MAX to MIN radius
            phase_time = cycle_position - 6
            phase_duration = 6
            ratio = 1 - (phase_time / phase_duration)
            radius = MIN_RADIUS + (MAX_RADIUS - MIN_RADIUS) * ratio
            print(f"**EXHALE:** Radius: {int(radius)}")
            
        # --- PHASE 4: PAUSE (12s to 14s) ---
        else:
            radius = MIN_RADIUS
            print(f"**PAUSE:** Radius: {int(radius)}")
            
        # (In a real application, you would draw the circle here)
        # For this example, we'll just wait a bit to see the output change
        time.sleep(0.1)

# To run this logic in a simple terminal environment:
main()