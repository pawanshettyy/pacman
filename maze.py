import pygame
from config import *

class Maze:
    def __init__(self):
        # Classic Pacman maze layout
        self.layout = [
            "###################",
            "#........#........#",
            "#o##.###.#.###.##o#",
            "#.................#",
            "#.##.#.#####.#.##.#",
            "#....#...#...#....#",
            "####.###.#.###.####",
            "   #.#.......#.#   ",
            "####.#.## ##.#.####",
            "#......#GGG#......#",
            "####.#.#GGG#.#.####",
            "   #.#.......#.#   ",
            "####.#.#####.#.####",
            "#........#........#",
            "#.##.###.#.###.##.#",
            "#o.#.....P.....#.o#",
            "##.#.#.#####.#.#.##",
            "#....#...#...#....#",
            "#.######.#.######.#",
            "#.................#",
            "###################"
        ]
        
        self.width = len(self.layout[0])
        self.height = len(self.layout)
        self.pellets = []
        self.power_pellets = []
        self.walls = []
        self.pacman_start = None
        self.ghost_starts = []
        
        self._parse_maze()
    
    def _parse_maze(self):
        """Parse the maze layout and create game objects"""
        for y, row in enumerate(self.layout):
            for x, cell in enumerate(row):
                pos = (x * CELL_SIZE, y * CELL_SIZE)
                
                if cell == WALL:
                    self.walls.append(pygame.Rect(pos[0], pos[1], CELL_SIZE, CELL_SIZE))
                elif cell == PELLET:
                    self.pellets.append(pygame.Rect(pos[0] + CELL_SIZE//2 - 2, 
                                                  pos[1] + CELL_SIZE//2 - 2, 4, 4))
                elif cell == POWER_PELLET:
                    self.power_pellets.append(pygame.Rect(pos[0] + CELL_SIZE//2 - 6, 
                                                        pos[1] + CELL_SIZE//2 - 6, 12, 12))
                elif cell == PACMAN_START:
                    self.pacman_start = (x, y)
                elif cell == GHOST_START:
                    self.ghost_starts.append((x, y))
    
    def is_wall(self, x, y):
        """Check if position is a wall"""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.layout[y][x] == WALL
        return True
    
    def is_valid_position(self, x, y):
        """Check if position is valid (not a wall)"""
        if 0 <= y < self.height and 0 <= x < self.width:
            cell = self.layout[y][x]
            return cell != WALL
        return False
    
    def get_cell(self, x, y):
        """Get the cell type at grid position"""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.layout[y][x]
        return WALL
    
    def draw(self, screen):
        """Draw the maze"""
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(screen, BLUE, wall)
        
        # Draw pellets
        for pellet in self.pellets:
            pygame.draw.rect(screen, YELLOW, pellet)
        
        # Draw power pellets
        for power_pellet in self.power_pellets:
            pygame.draw.ellipse(screen, YELLOW, power_pellet)
    
    def remove_pellet(self, rect):
        """Remove a pellet from the maze"""
        if rect in self.pellets:
            self.pellets.remove(rect)
            return PELLET_SCORE
        return 0
    
    def remove_power_pellet(self, rect):
        """Remove a power pellet from the maze"""
        if rect in self.power_pellets:
            self.power_pellets.remove(rect)
            return POWER_PELLET_SCORE
        return 0
    
    def all_pellets_eaten(self):
        """Check if all pellets have been eaten"""
        return len(self.pellets) == 0 and len(self.power_pellets) == 0
