import time
import math
from app_config import CONFIG

class BreathingState:
    """Manages the breathing cycle and light radius."""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        """Get time elapsed since start."""
        return time.time() - self.start_time
    
    def get_breathing_phase(self):
        """Returns the current breathing phase and progress."""
        t = self.get_elapsed_time()
        cycle_time = t % CONFIG['TOTAL_CYCLE']
        
        if cycle_time < CONFIG['INHALE_TIME']:
            phase = "INHALE"
            phase_time = cycle_time
            phase_duration = CONFIG['INHALE_TIME']
            phase_progress = phase_time / phase_duration
        elif cycle_time < CONFIG['INHALE_TIME'] + CONFIG['HOLD_AFTER_INHALE']:
            phase = "HOLD"
            phase_time = cycle_time - CONFIG['INHALE_TIME']
            phase_duration = CONFIG['HOLD_AFTER_INHALE']
            phase_progress = 1.0
        elif cycle_time < CONFIG['INHALE_TIME'] + CONFIG['HOLD_AFTER_INHALE'] + CONFIG['EXHALE_TIME']:
            phase = "EXHALE"
            phase_time = cycle_time - CONFIG['INHALE_TIME'] - CONFIG['HOLD_AFTER_INHALE']
            phase_duration = CONFIG['EXHALE_TIME']
            phase_progress = 1.0 - (phase_time / phase_duration)
        else:
            phase = "HOLD"
            phase_time = cycle_time - CONFIG['INHALE_TIME'] - CONFIG['HOLD_AFTER_INHALE'] - CONFIG['EXHALE_TIME']
            phase_duration = CONFIG['HOLD_AFTER_EXHALE']
            phase_progress = 0.0
        
        return {
            'phase': phase,
            'phase_time': phase_time,
            'phase_duration': phase_duration,
            'phase_progress': phase_progress
        }
    
    def get_current_radius(self):
        """Calculate current light radius based on breathing phase."""
        phase_data = self.get_breathing_phase()
        phase_progress = phase_data['phase_progress']
        smoothed = 0.5 - 0.5 * math.cos(phase_progress * math.pi)
        return CONFIG['MIN_LIGHT_RADIUS'] + (CONFIG['MAX_LIGHT_RADIUS'] - CONFIG['MIN_LIGHT_RADIUS']) * smoothed
    
    def get_cycle_number(self):
        """Get current cycle number."""
        return int(self.get_elapsed_time() // CONFIG['TOTAL_CYCLE']) + 1
    
    def to_dict(self):
        """Convert state to dictionary."""
        phase_data = self.get_breathing_phase()
        return {
            'phase': phase_data['phase'],
            'phase_time': phase_data['phase_time'],
            'phase_duration': phase_data['phase_duration'],
            'phase_progress': phase_data['phase_progress'],
            'current_radius': self.get_current_radius(),
            'cycle_number': self.get_cycle_number()
        }

