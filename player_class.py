import math
import random



class Player:
    """Manages player position and movement."""
    
    def __init__(self, start_row, start_col):
        self.row = start_row
        self.col = start_col
    
    def move(self, direction, maze):
        """Attempt to move player in given direction."""
        direction_map = {
            'up': (-1, 0),
            'down': (1, 0),
            'left': (0, -1),
            'right': (0, 1)
        }
        
        if direction not in direction_map:
            return False
        
        dr, dc = direction_map[direction]
        new_row = self.row + dr
        new_col = self.col + dc
        
        if 0 <= new_row < len(maze.layout) and 0 <= new_col < len(maze.layout[0]):
            if maze.get_cell(new_row, new_col) != '#':
                self.row = new_row
                self.col = new_col
                return True
        return False
    
    def to_dict(self):
        """Convert player to dictionary."""
        return {
            'row': self.row,
            'col': self.col
        }
    