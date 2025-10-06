import pygame
import sys
import math
from config import *
from maze import Maze
from pacman import Pacman
from ghost import Ghost

class Game:
    def __init__(self):
        print("Initializing pygame...")
        pygame.init()
        print("Creating display...")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman")
        self.clock = pygame.time.Clock()
        print("Loading fonts...")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = PLAYING
        self.score = 0
        self.lives = 3
        self.level = 1
        
        # Initialize game objects
        print("Creating maze...")
        self.maze = Maze()
        print(f"Maze created. Pacman start: {self.maze.pacman_start}, Ghost starts: {len(self.maze.ghost_starts)}")
        
        # Ensure Pacman has a valid start position
        if self.maze.pacman_start:
            print(f"Creating Pacman at position {self.maze.pacman_start}")
            self.pacman = Pacman(self.maze.pacman_start[0], self.maze.pacman_start[1], self.maze)
        else:
            # Default position if not found in maze
            print("Using default Pacman position")
            self.pacman = Pacman(9, 15, self.maze)
        
        # Create ghosts
        self.ghosts = []
        ghost_colors = [RED, PINK, CYAN, ORANGE]
        ghost_modes = ["chase", "scatter", "chase", "random"]
        
        # Use ghost start positions from maze, or default positions
        if self.maze.ghost_starts and len(self.maze.ghost_starts) >= 4:
            ghost_positions = self.maze.ghost_starts[:4]
        else:
            # Default positions in the ghost house area
            ghost_positions = [(9, 9), (10, 9), (9, 10), (10, 10)]
        
        print(f"Creating {len(ghost_positions)} ghosts...")
        for i, (color, mode) in enumerate(zip(ghost_colors, ghost_modes)):
            if i < len(ghost_positions):
                pos = ghost_positions[i]
                print(f"Creating ghost {i+1} at position {pos}")
                ghost = Ghost(pos[0], pos[1], color, self.maze, mode)
                self.ghosts.append(ghost)
        
        print(f"Game initialization complete! {len(self.ghosts)} ghosts created.")
        
        # Power pellet timer
        self.power_pellet_timer = 0
        
        # Game timing
        self.mode_timer = 0
        self.mode_duration = 7000  # 7 seconds
        self.scatter_mode = True
        
        # Performance optimization
        self.last_update_time = 0
        self.update_interval = 16  # ~60 FPS
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    if self.state == PLAYING:
                        self.state = PAUSED
                    elif self.state == PAUSED:
                        self.state = PLAYING
                elif event.key == pygame.K_r and self.state == GAME_OVER:
                    self.reset_game()
                
                # Handle movement on key press for immediate response
                elif self.state == PLAYING:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.pacman.set_direction(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.pacman.set_direction(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.pacman.set_direction(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.pacman.set_direction(RIGHT)
        
        # Also handle continuous key presses for smoother movement
        if self.state == PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.pacman.set_direction(UP)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.pacman.set_direction(DOWN)
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.pacman.set_direction(LEFT)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.pacman.set_direction(RIGHT)
        
        return True
    
    def update(self):
        """Update game logic"""
        if self.state != PLAYING:
            return
        
        # Update mode timer for ghost behavior
        self.mode_timer += self.clock.get_time()
        if self.mode_timer >= self.mode_duration:
            self.scatter_mode = not self.scatter_mode
            self.mode_timer = 0
            # Update ghost modes
            for ghost in self.ghosts:
                if not ghost.frightened and not ghost.eaten:
                    ghost.target_mode = "scatter" if self.scatter_mode else "chase"
        
        # Update power pellet timer
        if self.power_pellet_timer > 0:
            self.power_pellet_timer -= self.clock.get_time()
            if self.power_pellet_timer <= 0:
                # End frightened mode for all ghosts
                for ghost in self.ghosts:
                    ghost.frightened = False
        
        # Update Pacman
        self.pacman.update()
        
        # Update ghosts
        pacman_pos = self.pacman.get_grid_position()
        for ghost in self.ghosts:
            ghost.update(pacman_pos)
        
        # Check collisions
        self.check_collisions()
        
        # Check win condition
        if self.maze.all_pellets_eaten():
            self.next_level()
    
    def check_collisions(self):
        """Check for collisions between game objects"""
        # Get Pacman's grid position for more accurate collision detection
        pacman_grid_x = int(self.pacman.pixel_x // CELL_SIZE)
        pacman_grid_y = int(self.pacman.pixel_y // CELL_SIZE)
        
        # Check pellet collisions (more precise)
        for pellet in self.maze.pellets[:]:  # Use slice to avoid modification during iteration
            pellet_grid_x = int(pellet.x // CELL_SIZE)
            pellet_grid_y = int(pellet.y // CELL_SIZE)
            
            # Check if Pacman is in the same grid cell as pellet
            if (pacman_grid_x == pellet_grid_x and pacman_grid_y == pellet_grid_y):
                self.score += self.maze.remove_pellet(pellet)
        
        # Check power pellet collisions
        for power_pellet in self.maze.power_pellets[:]:
            power_pellet_grid_x = int(power_pellet.x // CELL_SIZE)
            power_pellet_grid_y = int(power_pellet.y // CELL_SIZE)
            
            if (pacman_grid_x == power_pellet_grid_x and pacman_grid_y == power_pellet_grid_y):
                self.score += self.maze.remove_power_pellet(power_pellet)
                # Activate power mode
                self.power_pellet_timer = POWER_PELLET_DURATION
                for ghost in self.ghosts:
                    if not ghost.eaten:
                        ghost.set_frightened(POWER_PELLET_DURATION // 16)  # Convert to frames
        
        # Check ghost collisions with distance-based detection
        for ghost in self.ghosts:
            distance = math.sqrt((self.pacman.pixel_x - ghost.pixel_x)**2 + 
                               (self.pacman.pixel_y - ghost.pixel_y)**2)
            
            if distance < (self.pacman.radius + ghost.radius - 5):  # Slight overlap tolerance
                if ghost.frightened and not ghost.eaten:
                    # Eat the ghost
                    ghost.eat()
                    self.score += GHOST_SCORE
                elif not ghost.eaten:
                    # Pacman dies
                    self.pacman_dies()
    
    def pacman_dies(self):
        """Handle Pacman death"""
        self.lives -= 1
        if self.lives <= 0:
            self.state = GAME_OVER
        else:
            # Reset positions
            self.pacman.reset_position()
            for ghost in self.ghosts:
                ghost.reset_position()
            self.power_pellet_timer = 0
    
    def next_level(self):
        """Advance to next level"""
        self.level += 1
        self.score += BONUS_SCORE
        
        # Reset maze and positions
        self.maze = Maze()
        self.pacman.maze = self.maze
        if self.maze.pacman_start:
            self.pacman.grid_x, self.pacman.grid_y = self.maze.pacman_start
            self.pacman.pixel_x = self.pacman.grid_x * CELL_SIZE + CELL_SIZE // 2
            self.pacman.pixel_y = self.pacman.grid_y * CELL_SIZE + CELL_SIZE // 2
        self.pacman.reset_position()
        
        # Reset ghosts with new positions
        ghost_positions = self.maze.ghost_starts[:4] if self.maze.ghost_starts and len(self.maze.ghost_starts) >= 4 else [(9, 9), (10, 9), (9, 10), (10, 10)]
        for i, ghost in enumerate(self.ghosts):
            ghost.maze = self.maze
            if i < len(ghost_positions):
                ghost.start_x, ghost.start_y = ghost_positions[i]
            ghost.reset_position()
            # Increase ghost speed slightly
            ghost.speed = min(ghost.speed + 0.1, PACMAN_SPEED - 0.5)
        
        self.power_pellet_timer = 0
        self.mode_timer = 0
        self.scatter_mode = True
    
    def reset_game(self):
        """Reset the entire game"""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.state = PLAYING
        
        # Reset maze and positions
        self.maze = Maze()
        self.pacman.maze = self.maze
        if self.maze.pacman_start:
            self.pacman.grid_x, self.pacman.grid_y = self.maze.pacman_start
            self.pacman.pixel_x = self.pacman.grid_x * CELL_SIZE + CELL_SIZE // 2
            self.pacman.pixel_y = self.pacman.grid_y * CELL_SIZE + CELL_SIZE // 2
        self.pacman.reset_position()
        
        # Reset ghosts with new positions
        ghost_positions = self.maze.ghost_starts[:4] if self.maze.ghost_starts and len(self.maze.ghost_starts) >= 4 else [(9, 9), (10, 9), (9, 10), (10, 10)]
        for i, ghost in enumerate(self.ghosts):
            ghost.maze = self.maze
            if i < len(ghost_positions):
                ghost.start_x, ghost.start_y = ghost_positions[i]
            ghost.reset_position()
            ghost.speed = GHOST_SPEED
        
        self.power_pellet_timer = 0
        self.mode_timer = 0
        self.scatter_mode = True
    
    def draw(self):
        """Draw everything on screen"""
        self.screen.fill(BLACK)
        
        # Draw maze
        self.maze.draw(self.screen)
        
        # Draw Pacman
        self.pacman.draw(self.screen)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw game state overlays
        if self.state == PAUSED:
            self.draw_pause_screen()
        elif self.state == GAME_OVER:
            self.draw_game_over_screen()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw user interface elements"""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
        
        # Level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 90))
        
        # Power pellet indicator
        if self.power_pellet_timer > 0:
            power_text = self.small_font.render("POWER MODE!", True, YELLOW)
            self.screen.blit(power_text, (SCREEN_WIDTH - 120, 10))
    
    def draw_pause_screen(self):
        """Draw pause screen overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(pause_text, text_rect)
        
        continue_text = self.small_font.render("Press SPACE to continue", True, WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_game_over_screen(self):
        """Draw game over screen overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        self.screen.blit(game_over_text, text_rect)
        
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.small_font.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Main game loop"""
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = current_time - last_time
            last_time = current_time
            
            # Cap delta time to prevent large jumps
            dt = min(dt, 50)  # Maximum 50ms per frame
            
            running = self.handle_events()
            self.update()
            self.draw()
            
            # More consistent frame rate
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
