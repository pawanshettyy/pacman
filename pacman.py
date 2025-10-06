import pygame
import math
from config import *

class Pacman:
    def __init__(self, x, y, maze):
        self.maze = maze
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = y * CELL_SIZE + CELL_SIZE // 2
        self.direction = STOP
        self.next_direction = STOP
        self.speed = PACMAN_SPEED
        self.radius = 12
        self.mouth_angle = 0
        self.mouth_speed = 8
        self.rect = pygame.Rect(self.pixel_x - self.radius, self.pixel_y - self.radius, 
                               self.radius * 2, self.radius * 2)
    
    def update(self):
        """Update Pacman's position and animation"""
        # Store previous position for collision checking
        prev_x, prev_y = self.pixel_x, self.pixel_y
        
        # Check if we can change direction (more responsive)
        if self.next_direction != STOP:
            # Calculate where we would be if we changed direction
            test_x = self.pixel_x + self.next_direction[0] * self.speed
            test_y = self.pixel_y + self.next_direction[1] * self.speed
            
            # Convert to grid coordinates
            next_grid_x = int(test_x // CELL_SIZE)
            next_grid_y = int(test_y // CELL_SIZE)
            
            # Allow direction change if the new direction is valid
            if self.maze.is_valid_position(next_grid_x, next_grid_y):
                # For better responsiveness, allow direction change when close to grid center
                if self._is_near_grid_center() or self.direction == STOP:
                    self.direction = self.next_direction
                    self.next_direction = STOP
                    # Snap to grid center for cleaner movement
                    self._snap_to_grid_center()
        
        # Move Pacman continuously
        if self.direction != STOP:
            # Calculate next position
            next_x = self.pixel_x + self.direction[0] * self.speed
            next_y = self.pixel_y + self.direction[1] * self.speed
            
            # Calculate which grid cells we'll be occupying
            left_grid = int((next_x - self.radius) // CELL_SIZE)
            right_grid = int((next_x + self.radius) // CELL_SIZE)
            top_grid = int((next_y - self.radius) // CELL_SIZE)
            bottom_grid = int((next_y + self.radius) // CELL_SIZE)
            
            # Check if all occupied cells are valid
            can_move = True
            for gx in range(left_grid, right_grid + 1):
                for gy in range(top_grid, bottom_grid + 1):
                    if not self.maze.is_valid_position(gx, gy):
                        can_move = False
                        break
                if not can_move:
                    break
            
            if can_move:
                self.pixel_x = next_x
                self.pixel_y = next_y
            else:
                # Stop movement and snap to grid center
                self.direction = STOP
                self._snap_to_grid_center()
        
        # Handle screen wrapping (tunnel effect)
        if self.pixel_x < -self.radius:
            self.pixel_x = SCREEN_WIDTH + self.radius
        elif self.pixel_x > SCREEN_WIDTH + self.radius:
            self.pixel_x = -self.radius
        
        # Update grid position
        self.grid_x = int(self.pixel_x // CELL_SIZE)
        self.grid_y = int(self.pixel_y // CELL_SIZE)
        
        # Update rectangle for collision detection
        self.rect.center = (int(self.pixel_x), int(self.pixel_y))
        
        # Update mouth animation (only when moving)
        if self.direction != STOP:
            self.mouth_angle += self.mouth_speed
            if self.mouth_angle > 45:
                self.mouth_speed = -self.mouth_speed
            elif self.mouth_angle < 0:
                self.mouth_speed = -self.mouth_speed
        else:
            # Close mouth when stopped
            self.mouth_angle = max(0, self.mouth_angle - 4)
    
    def _is_near_grid_center(self):
        """Check if Pacman is near the center of a grid cell for responsive direction changes"""
        center_x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
        center_y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
        return abs(self.pixel_x - center_x) < MOVEMENT_THRESHOLD and abs(self.pixel_y - center_y) < MOVEMENT_THRESHOLD
    
    def _snap_to_grid_center(self):
        """Snap Pacman to the center of current grid cell"""
        self.pixel_x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
    
    def set_direction(self, direction):
        """Set the next direction for Pacman"""
        self.next_direction = direction
    
    def draw(self, screen):
        """Draw Pacman with mouth animation"""
        # Determine rotation based on direction
        rotation = 0
        if self.direction == LEFT:
            rotation = 180
        elif self.direction == UP:
            rotation = 90
        elif self.direction == DOWN:
            rotation = 270
        
        # Calculate mouth angles
        start_angle = math.radians(rotation + self.mouth_angle)
        end_angle = math.radians(rotation - self.mouth_angle)
        
        # Draw Pacman body
        if self.direction == STOP or self.mouth_angle <= 0:
            # Draw full circle when stopped or mouth closed
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.pixel_x), int(self.pixel_y)), self.radius)
        else:
            # Draw Pacman with mouth
            points = [(int(self.pixel_x), int(self.pixel_y))]
            
            # Create arc points
            for angle in range(int(math.degrees(start_angle)), 
                             int(math.degrees(end_angle)) + 1):
                x = self.pixel_x + self.radius * math.cos(math.radians(angle))
                y = self.pixel_y + self.radius * math.sin(math.radians(angle))
                points.append((int(x), int(y)))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, YELLOW, points)
            else:
                pygame.draw.circle(screen, YELLOW, 
                                 (int(self.pixel_x), int(self.pixel_y)), self.radius)
        
        # Draw eye
        eye_offset = 4
        if self.direction == RIGHT or self.direction == STOP:
            eye_x = self.pixel_x + eye_offset
            eye_y = self.pixel_y - eye_offset
        elif self.direction == LEFT:
            eye_x = self.pixel_x - eye_offset
            eye_y = self.pixel_y - eye_offset
        elif self.direction == UP:
            eye_x = self.pixel_x + eye_offset
            eye_y = self.pixel_y - eye_offset
        else:  # DOWN
            eye_x = self.pixel_x + eye_offset
            eye_y = self.pixel_y + eye_offset
        
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 2)
    
    def get_grid_position(self):
        """Get current grid position"""
        return (self.grid_x, self.grid_y)
    
    def reset_position(self):
        """Reset Pacman to starting position"""
        if self.maze.pacman_start:
            self.grid_x, self.grid_y = self.maze.pacman_start
            self.pixel_x = self.grid_x * CELL_SIZE + CELL_SIZE // 2
            self.pixel_y = self.grid_y * CELL_SIZE + CELL_SIZE // 2
            self.direction = STOP
            self.next_direction = STOP
            self.rect.center = (self.pixel_x, self.pixel_y)
