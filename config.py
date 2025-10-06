# Game Configuration and Constants

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 900
MAZE_WIDTH = 19
MAZE_HEIGHT = 21
CELL_SIZE = 30

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)

# Game settings
FPS = 60
PACMAN_SPEED = 4
GHOST_SPEED = 3
POWER_PELLET_DURATION = 8000  # milliseconds
MOVEMENT_THRESHOLD = 2  # Pixels to consider "close enough" to grid center

# Scoring
PELLET_SCORE = 10
POWER_PELLET_SCORE = 50
GHOST_SCORE = 200
BONUS_SCORE = 1000

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
PAUSED = 3
LEVEL_COMPLETE = 4

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
STOP = (0, 0)

# Maze symbols
WALL = '#'
PELLET = '.'
POWER_PELLET = 'o'
EMPTY = ' '
PACMAN_START = 'P'
GHOST_START = 'G'
GHOST_HOUSE = 'H'
