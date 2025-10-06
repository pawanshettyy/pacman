#!/usr/bin/env python3
"""
Simple test to run a minimal version of the game
"""

import pygame
import sys
from config import *
from maze import Maze
from pacman import Pacman
from ghost import Ghost

def main():
    try:
        print("Initializing pygame...")
        pygame.init()
        
        print("Creating screen...")
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman Test")
        clock = pygame.time.Clock()
        
        print("Creating game objects...")
        maze = Maze()
        
        # Create Pacman
        if maze.pacman_start:
            pacman = Pacman(maze.pacman_start[0], maze.pacman_start[1], maze)
        else:
            pacman = Pacman(9, 15, maze)
        
        # Create one ghost for testing
        ghost = Ghost(9, 9, RED, maze, "chase")
        
        print("Starting game loop...")
        running = True
        frame_count = 0
        
        while running and frame_count < 300:  # Run for 5 seconds at 60 FPS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # Handle input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                pacman.set_direction(UP)
            elif keys[pygame.K_DOWN]:
                pacman.set_direction(DOWN)
            elif keys[pygame.K_LEFT]:
                pacman.set_direction(LEFT)
            elif keys[pygame.K_RIGHT]:
                pacman.set_direction(RIGHT)
            
            # Update
            pacman.update()
            ghost.update(pacman.get_grid_position())
            
            # Draw
            screen.fill(BLACK)
            maze.draw(screen)
            pacman.draw(screen)
            ghost.draw(screen)
            
            pygame.display.flip()
            clock.tick(FPS)
            frame_count += 1
        
        print("Test completed successfully!")
        pygame.quit()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()

if __name__ == "__main__":
    main()
