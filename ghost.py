import pygame
import random
import math
from config import *

class Ghost:
    def __init__(self, x, y, color, maze, target_mode="random"):
        self.maze = maze
        self.start_x = x
        self.start_y = y
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = y * CELL_SIZE + CELL_SIZE // 2
        self.color = color
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.speed = GHOST_SPEED
        self.radius = 12
        self.target_mode = target_mode
        self.frightened = False
        self.frightened_timer = 0
        self.eaten = False
        self.rect = pygame.Rect(self.pixel_x - self.radius, self.pixel_y - self.radius,
                               self.radius * 2, self.radius * 2)
    
    def update(self, pacman_pos):
        """Update ghost position and AI"""
        if self.eaten:
            # Return to start position when eaten
            self._return_to_start()
        else:
            # Normal movement
            self._move(pacman_pos)
        
        # Update frightened state
        if self.frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.frightened = False
        
        # Update rectangle for collision detection
        self.rect.center = (self.pixel_x, self.pixel_y)
    
    def _move(self, pacman_pos):
        """Move the ghost based on AI behavior"""
        # Check if we need to choose a new direction (when at intersection)
        if self._is_near_grid_center():
            possible_directions = self._get_possible_directions()
            
            if len(possible_directions) > 1:  # At an intersection
                if self.frightened:
                    # Random movement when frightened, but avoid reversing
                    available = [d for d in possible_directions if d != (-self.direction[0], -self.direction[1])]
                    if available:
                        self.direction = random.choice(available)
                    else:
                        self.direction = random.choice(possible_directions)
                else:
                    # Choose direction based on target
                    self.direction = self._choose_direction(possible_directions, pacman_pos)
            elif len(possible_directions) == 1:
                # Only one way to go (dead end or forced turn)
                self.direction = possible_directions[0]
        
        # Move in current direction
        if self.direction != STOP:
            next_x = self.pixel_x + self.direction[0] * self.speed
            next_y = self.pixel_y + self.direction[1] * self.speed
            
            # Calculate which grid cells we'll be occupying
            left_grid = int((next_x - self.radius) // CELL_SIZE)
            right_grid = int((next_x + self.radius) // CELL_SIZE)
            top_grid = int((next_y - self.radius) // CELL_SIZE)
            bottom_grid = int((next_y + self.radius) // CELL_SIZE)
            
            # Check if all occupied cells are valid (or ghost areas)
            can_move = True
            for gx in range(left_grid, right_grid + 1):
                for gy in range(top_grid, bottom_grid + 1):
                    if not (self.maze.is_valid_position(gx, gy) or 
                           (hasattr(self.maze, 'get_cell') and self.maze.get_cell(gx, gy) in ['G', 'H'])):
                        can_move = False
                        break
                if not can_move:
                    break
            
            if can_move:
                self.pixel_x = next_x
                self.pixel_y = next_y
            else:
                # Try to find a valid direction
                possible_directions = self._get_possible_directions()
                if possible_directions:
                    self.direction = possible_directions[0]
        
        # Handle screen wrapping
        if self.pixel_x < -self.radius:
            self.pixel_x = SCREEN_WIDTH + self.radius
        elif self.pixel_x > SCREEN_WIDTH + self.radius:
            self.pixel_x = -self.radius
        
        # Update grid position
        self.grid_x = int(self.pixel_x // CELL_SIZE)
        self.grid_y = int(self.pixel_y // CELL_SIZE)
    
    def _is_near_grid_center(self):
        """Check if ghost is near the center of a grid cell"""
        center_x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
        return abs(self.pixel_x - center_x) < MOVEMENT_THRESHOLD and abs(self.pixel_y - center_y) < MOVEMENT_THRESHOLD
    
    def _get_possible_directions(self):
        """Get list of valid directions from current position"""
        directions = []
        for direction in [UP, DOWN, LEFT, RIGHT]:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]
            if self.maze.is_valid_position(next_x, next_y):
                # Don't reverse direction unless it's the only option
                reverse_dir = (-self.direction[0], -self.direction[1])
                if direction != reverse_dir or len(directions) == 0:
                    directions.append(direction)
        
        # If no forward directions available, allow reverse
        if not directions:
            reverse_dir = (-self.direction[0], -self.direction[1])
            next_x = self.grid_x + reverse_dir[0]
            next_y = self.grid_y + reverse_dir[1]
            if self.maze.is_valid_position(next_x, next_y):
                directions.append(reverse_dir)
        
        return directions
    
    def _choose_direction(self, possible_directions, pacman_pos):
        """Choose direction based on AI behavior"""
        if self.target_mode == "chase":
            return self._chase_pacman(possible_directions, pacman_pos)
        elif self.target_mode == "scatter":
            return self._scatter_behavior(possible_directions)
        else:
            return random.choice(possible_directions)
    
    def _chase_pacman(self, possible_directions, pacman_pos):
        """Chase Pacman directly"""
        pacman_x, pacman_y = pacman_pos
        min_distance = float('inf')
        best_direction = possible_directions[0]
        
        for direction in possible_directions:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]
            distance = math.sqrt((next_x - pacman_x)**2 + (next_y - pacman_y)**2)
            
            if distance < min_distance:
                min_distance = distance
                best_direction = direction
        
        return best_direction
    
    def _scatter_behavior(self, possible_directions):
        """Scatter to corners"""
        # Target corners based on ghost color
        if self.color == RED:
            target = (0, 0)  # Top-left
        elif self.color == PINK:
            target = (18, 0)  # Top-right
        elif self.color == CYAN:
            target = (0, 20)  # Bottom-left
        else:
            target = (18, 20)  # Bottom-right
        
        min_distance = float('inf')
        best_direction = possible_directions[0]
        
        for direction in possible_directions:
            next_x = self.grid_x + direction[0]
            next_y = self.grid_y + direction[1]
            distance = math.sqrt((next_x - target[0])**2 + (next_y - target[1])**2)
            
            if distance < min_distance:
                min_distance = distance
                best_direction = direction
        
        return best_direction
    
    def _return_to_start(self):
        """Return to starting position when eaten"""
        target_x = self.start_x * CELL_SIZE + CELL_SIZE // 2
        target_y = self.start_y * CELL_SIZE + CELL_SIZE // 2
        
        dx = target_x - self.pixel_x
        dy = target_y - self.pixel_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 5:
            self.eaten = False
            self.pixel_x = target_x
            self.pixel_y = target_y
            self.grid_x = self.start_x
            self.grid_y = self.start_y
        else:
            # Move towards start position
            if distance > 0:
                self.pixel_x += (dx / distance) * self.speed * 2
                self.pixel_y += (dy / distance) * self.speed * 2
    
    def set_frightened(self, duration):
        """Set ghost to frightened state"""
        self.frightened = True
        self.frightened_timer = duration
    
    def eat(self):
        """Mark ghost as eaten"""
        self.eaten = True
        self.frightened = False
    
    def draw(self, screen):
        """Draw the ghost"""
        if self.eaten:
            # Draw eyes only when eaten
            pygame.draw.circle(screen, WHITE, 
                             (int(self.pixel_x - 4), int(self.pixel_y - 2)), 3)
            pygame.draw.circle(screen, WHITE, 
                             (int(self.pixel_x + 4), int(self.pixel_y - 2)), 3)
            pygame.draw.circle(screen, BLACK, 
                             (int(self.pixel_x - 4), int(self.pixel_y - 2)), 1)
            pygame.draw.circle(screen, BLACK, 
                             (int(self.pixel_x + 4), int(self.pixel_y - 2)), 1)
        else:
            # Draw ghost body
            color = BLUE if self.frightened else self.color
            
            # Ghost body (circle top, wavy bottom)
            pygame.draw.circle(screen, color, 
                             (int(self.pixel_x), int(self.pixel_y - 2)), self.radius)
            
            # Ghost bottom (rectangle with wavy edge)
            bottom_rect = pygame.Rect(self.pixel_x - self.radius, self.pixel_y - 2,
                                    self.radius * 2, self.radius + 2)
            pygame.draw.rect(screen, color, bottom_rect)
            
            # Wavy bottom edge
            wave_points = []
            for i in range(5):
                x = self.pixel_x - self.radius + (i * self.radius // 2)
                y = self.pixel_y + self.radius - (2 if i % 2 == 0 else -2)
                wave_points.append((x, y))
            
            if len(wave_points) > 2:
                pygame.draw.polygon(screen, color, wave_points)
            
            # Eyes
            if not self.frightened:
                # Normal eyes
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.pixel_x - 4), int(self.pixel_y - 2)), 3)
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.pixel_x + 4), int(self.pixel_y - 2)), 3)
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.pixel_x - 4), int(self.pixel_y - 2)), 1)
                pygame.draw.circle(screen, BLACK, 
                                 (int(self.pixel_x + 4), int(self.pixel_y - 2)), 1)
            else:
                # Frightened eyes (dots)
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.pixel_x - 3), int(self.pixel_y)), 2)
                pygame.draw.circle(screen, WHITE, 
                                 (int(self.pixel_x + 3), int(self.pixel_y)), 2)
    
    def get_grid_position(self):
        """Get current grid position"""
        return (self.grid_x, self.grid_y)
    
    def reset_position(self):
        """Reset ghost to starting position"""
        self.grid_x = self.start_x
        self.grid_y = self.start_y
        self.pixel_x = self.start_x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = self.start_y * CELL_SIZE + CELL_SIZE // 2
        self.frightened = False
        self.frightened_timer = 0
        self.eaten = False
        self.rect.center = (self.pixel_x, self.pixel_y)
