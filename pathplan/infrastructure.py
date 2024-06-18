import pygame
import math
from queue import PriorityQueue

# color
GRID_COLOR = (128, 128, 128)  
DEFAULT_NODE_COLOR = (255, 255, 255) 
BARRIER_COLOR = (0, 0, 0)  
CLOSED_COLOR = (192, 192, 192)  
END_COLOR = (143, 201, 58)  
PATH_COLOR = (0, 0, 255)  
START_COLOR = (255, 0, 0)  
OPEN_COLOR = (90, 90, 90) 

# Node 
class Node:
    def __init__(self, row, col, width):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.width = width
        self.color = DEFAULT_NODE_COLOR

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def get_pos(self):
        return self.row, self.col

    def draw(self):
        pygame.draw.rect(WIN, self.color, (self.x, self.y, self.width, self.width ))
        
    def update_neighbors(self, grid):
            self.neighbors = []
            if self.row < ROWCOL - 1 and  grid[self.row + 1][self.col].get_color()!=BARRIER_COLOR:#Down
                self.neighbors.append(grid[self.row + 1][self.col])

            if self.row > 0 and grid[self.row - 1][self.col].get_color()!=BARRIER_COLOR:#Up
                self.neighbors.append(grid[self.row - 1][self.col])
                
            if self.col < ROWCOL - 1 and grid[self.row][self.col+1].get_color()!=BARRIER_COLOR: #Right
                self.neighbors.append(grid[self.row][self.col+1])

            if self.col > 0 and grid[self.row][self.col - 1].get_color()!=BARRIER_COLOR: #Left
                self.neighbors.append(grid[self.row][self.col - 1])

def draw(grid):
    WIN.fill(DEFAULT_NODE_COLOR)
    for row in grid:
        for node in row:
            node.draw()
    draw_grid()
    pygame.display.update()
def draw_grid():
    gap = WIDTH // ROWCOL

    for row in range(ROWCOL):
        pygame.draw.line(WIN, GRID_COLOR, (0, row * gap), (WIDTH, row * gap))
        for col in range(ROWCOL):
            pygame.draw.line(WIN, GRID_COLOR, (col * gap, 0), (col * gap, WIDTH))
         
#Canvas setting up (Do not change these parameters)
WIDTH = 700
ROWCOL = 50

WIN = pygame.display.set_mode((WIDTH,WIDTH))

def make_grid(default_start_pos, default_end_pos, barrier_positions):
    grid = []
    nodeWidth = WIDTH // ROWCOL
    for row in range(ROWCOL):
        grid.append([])
        for col in range(ROWCOL):
            node = Node(row, col, nodeWidth)
            grid[row].append(node)
            if (row, col) in barrier_positions:
                node.set_color(BARRIER_COLOR) 

    grid[default_start_pos[0]][default_start_pos[1]].set_color(START_COLOR)
    grid[default_end_pos[0]][default_end_pos[1]].set_color(END_COLOR)
    return grid, grid[default_start_pos[0]][default_start_pos[1]], grid[default_end_pos[0]][default_end_pos[1]]

def display_text(screen, text, position, font_size=30, color=(0, 0, 0)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

# def draw_status(screen):
#     display_text(screen, "Status:", (10, 10))
#     display_text(screen, "Path Length:", (10, 45))
#     display_text(screen, "Visited Nodes", (10, 80))
#     display_text(screen, "Queue Size:", (10, 115))
#     pygame.display.update()

#FIXME buggy ui related function
def setup_fixed_text(screen):
    font_size = 30
    font = pygame.font.Font(None, font_size)
    labels = ["Status:", "Path Length:", "Visited Nodes:", "Queue Size:"]
    positions = [(10, WIDTH + 20), (10, WIDTH + 55), (10, WIDTH + 90), (10, WIDTH + 125)]
    for label, position in zip(labels, positions):
        text_surface = font.render(label, True, (0, 0, 0))
        screen.blit(text_surface, position)
    pygame.display.update()
