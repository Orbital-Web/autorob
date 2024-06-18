from infrastructure import GRID_COLOR,DEFAULT_NODE_COLOR,BARRIER_COLOR,CLOSED_COLOR ,END_COLOR,PATH_COLOR,START_COLOR,OPEN_COLOR,WIDTH,ROWCOL,draw,make_grid,display_text,setup_fixed_text
import pygame
import argparse

def get_args():
    parser = argparse.ArgumentParser(description="Visualize different pathfinding algorithms on various canvas types.")
    parser.add_argument('-algorithm', type=str, choices=['astar', 'rrt'], default='astar', help='Specify the search algorithm (astar or rrt)')
    parser.add_argument('-map', type=str, choices=['empty', 'misc', 'narrow1', 'narrow2', 'three_section'], default='empty', help='Type of canvas to display')
    return parser.parse_args()

def get_algorithm(algorithm):
    if algorithm == 'astar':
        print("Running A* algorithm...")
        pygame.display.set_caption("A* algorithm visualizer")
        from astar import astar_algorithm
        return astar_algorithm
    elif algorithm == 'rrt':
        print("Running RRT algorithm...")
        pygame.display.set_caption("RRT algorithm visualizer")
        # TODO implement RRT algorithm
    else:
        print("Algorithm not recognized")
        return None  
 
def get_map(map_type):
    if map_type == 'empty':
        default_start_pos = (5, 5) 
        default_end_pos = (ROWCOL - 5, ROWCOL - 5)  
        barrier_positions = []  
        return make_grid(default_start_pos, default_end_pos, barrier_positions)
    elif map_type == 'misc':
        # TODO misc implement
        return 
    elif map_type == 'narrow1':
        # TODO narrow1 implement
        return
    elif map_type == 'narrow2':
        # TODO narrow2 implement
        return 
    elif map_type == 'three_section':
        # TODO three_section implement
        return 
    else:
        print("Canvas not recognized")

def reset(grid,all = False, keep_start = False):
    for row in grid:
        for node in row:
            color = node.get_color()
            if all:
                node.set_color(DEFAULT_NODE_COLOR)
            elif keep_start:
                if color == OPEN_COLOR or color == CLOSED_COLOR or color == PATH_COLOR or color == END_COLOR: 
                    node.set_color(DEFAULT_NODE_COLOR)
            else:
                if color == OPEN_COLOR or color == CLOSED_COLOR or color == PATH_COLOR: 
                    node.set_color(DEFAULT_NODE_COLOR)
            
def get_clicked_pos(pos):
    gap = WIDTH // ROWCOL
    x,y = pos

    row = x // gap
    col = y // gap

    return row, col

def main(algorithm,map):
    #init search algorithm
    plan = get_algorithm(algorithm)
    if not plan:
        print("No valid planning algorithm found. Exiting.")
        return 
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WIDTH))

    running = True
    usedPreviously = False

    grid, start, end = get_map(map)
    if (not grid) or (not start) or (not end):
        print("No valid Canvas found. Exiting.")
        return 
    
    #status tracking variables 
    status = "Idle"
    path_length = 0
    visited_count = 0
    queue_size = 0
    def update_ui(new_status, new_path_length, new_visited_count, new_queue_size):
        nonlocal status, path_length, visited_count, queue_size
        # status, path_length, visited_count, queue_size = new_status, new_path_length, new_visited_count, new_queue_size
        # font_size = 30
        # font = pygame.font.Font(None, font_size)
        # values = [status, str(path_length), str(visited_count), str(queue_size)]
        # positions = [(120, WIDTH + 20), (120, WIDTH + 55), (120, WIDTH + 90), (120, WIDTH + 125)]
        # for value, position in zip(values, positions):
        #     clear_rect = pygame.Rect(position[0], position[1], 200, font_size)  # Adjust width as necessary
        #     screen.fill((0, 0, 0), clear_rect)  
        #     text_surface = font.render(value, True, (255, 255, 255))
        #     screen.blit(text_surface, position)
        # pygame.display.update()
        # FIXME buggy update ui 
        return
    while(running):
        draw(grid)
        # status update
        update_ui(status, path_length, visited_count, queue_size)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # select start point ,end point and barrier
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                if start == None :
                    node.set_color(START_COLOR)
                    start = node
                elif (end == None and node != start):
                    node.set_color(END_COLOR)
                    end = node
                elif node != end and node != start :
                    node.set_color(BARRIER_COLOR)
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                node.set_color(DEFAULT_NODE_COLOR)

                if node == start:
                    start = None
                elif node == end:
                    end = None

            elif event.type == pygame.KEYDOWN:
                #use space to start your planning algorithm
                if event.key == pygame.K_SPACE and start and end:
                    if usedPreviously:
                        reset(grid)
                        visited_count = 0
                        queue_size = 0
                        path_length = 0
                        status = "Iterating"
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)
                    result = plan(lambda : draw(grid),update_ui, grid, start, end)
                    usedPreviously = True
                    status, path_length,visited_count,queue_size = result[0], result[1],result[2],result[3]
                #use C to clean the canvas(rerun algorithm)
                elif event.key == pygame.K_c:
                    usedPreviously = False
                    end = None
                    reset(grid, keep_start = True)
                    grid, start, end = get_map(map)
                    status = "Canvas Reset"
                    visited_count = 0
                    queue_size = 0
                    path_length = 0
                #use D to clean only all canvas (make own canvas)
                elif event.key == pygame.K_d:
                    usedPreviously = False
                    start = None
                    end = None
                    # clean the canvas including start, end and barriers
                    reset(grid,all = True)
                    status = "Create your own map"
                    visited_count = 0
                    queue_size = 0
                    path_length = 0
                # use E to change the end only
                # TODO
                    
    pygame.quit()          

if __name__ == "__main__":
    args = get_args()
    main(args.algorithm,args.map)