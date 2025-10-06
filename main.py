#!/usr/bin/env python3
"""
Pacman Game - Main Entry Point

A classic Pacman game implementation using Python and Pygame.
Use arrow keys or WASD to move Pacman around the maze.
Collect all pellets while avoiding ghosts!

Controls:
- Arrow keys or WASD: Move Pacman
- SPACE: Pause/Unpause
- ESC: Quit game
- R: Restart (when game over)
"""

from game import Game

def main():
    """Main function to start the game"""
    try:
        print("Initializing Pacman game...")
        game = Game()
        print("Game initialized successfully!")
        print("Starting game loop...")
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Make sure you have pygame installed: pip install pygame")

if __name__ == "__main__":
    main()
