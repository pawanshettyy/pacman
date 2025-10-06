#!/usr/bin/env python3
"""
Test script to check if the game initializes correctly
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing imports...")
    from config import *
    print("Config imported successfully")
    
    from maze import Maze
    print("Maze imported successfully")
    
    from pacman import Pacman
    print("Pacman imported successfully")
    
    from ghost import Ghost
    print("Ghost imported successfully")
    
    from game import Game
    print("Game imported successfully")
    
    print("\nTesting maze creation...")
    maze = Maze()
    print(f"Maze created: {maze.width}x{maze.height}")
    print(f"Pacman start: {maze.pacman_start}")
    print(f"Ghost starts: {maze.ghost_starts}")
    print(f"Pellets: {len(maze.pellets)}")
    print(f"Power pellets: {len(maze.power_pellets)}")
    
    print("\nTesting Pacman creation...")
    if maze.pacman_start:
        pacman = Pacman(maze.pacman_start[0], maze.pacman_start[1], maze)
        print(f"Pacman created at {pacman.grid_x}, {pacman.grid_y}")
    
    print("\nTesting Ghost creation...")
    ghost_positions = maze.ghost_starts[:4] if maze.ghost_starts and len(maze.ghost_starts) >= 4 else [(9, 9), (10, 9), (9, 10), (10, 10)]
    for i, pos in enumerate(ghost_positions):
        ghost = Ghost(pos[0], pos[1], RED, maze, "chase")
        print(f"Ghost {i+1} created at {ghost.grid_x}, {ghost.grid_y}")
    
    print("\nAll tests passed! The game components are working correctly.")
    
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()
