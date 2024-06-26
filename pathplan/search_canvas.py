from infrastructure import GRID_COLOR,DEFAULT_NODE_COLOR,BARRIER_COLOR,CLOSED_COLOR ,END_COLOR,PATH_COLOR,START_COLOR,OPEN_COLOR,WIDTH,ROWCOL,draw,make_grid,display_text,setup_fixed_text,Node
import pygame
import argparse
import json
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
        return load_map("scenes/misc.json")
    elif map_type == 'narrow1':
        return load_map("scenes/narrow1.json")
    elif map_type == 'narrow2':
        return load_map("scenes/narrow2.json")
    elif map_type == 'three_section':
        return load_map("scenes/three_section.json")
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
def save_map(grid, filename='map.json'):
    grid_data = []
    for row in grid:
        row_data = []
        for node in row:
            node_data = {
                'color': node.get_color(),
                'position': (node.row, node.col)
            }
            row_data.append(node_data)
        grid_data.append(row_data)

    map_data = {
        'grid': grid_data,
        'width': WIDTH,
        'rowcol': ROWCOL
    }

    with open(filename, 'w') as f:
        json.dump(map_data, f, indent=4)

def load_map(filename):
    with open(filename, 'r') as f:
        map_data = json.load(f)
    
    grid_data = map_data['grid']
    grid = []
    start = None
    end = None
    nodeWidth = WIDTH // ROWCOL

    for row_data in grid_data:
        row = []
        for node_data in row_data:
            node = Node(node_data['position'][0], node_data['position'][1], nodeWidth)
            node.set_color(tuple(node_data['color']))
            if node.get_color() == START_COLOR:
                start = node
            elif node.get_color() == END_COLOR:
                end = node
            row.append(node)
        grid.append(row)

    return grid, start, end

def get_clicked_pos(pos):
    gap = WIDTH // ROWCOL
    x,y = pos

    row = x // gap
    col = y // gap

    return row, col

def update_ui(screen, status, path_length, visited_count, queue_size):
    if not hasattr(update_ui, 'last_status'):
        update_ui.last_status = ""
        update_ui.last_path_length = 0
        update_ui.last_visited_count = 0
        update_ui.last_queue_size = 0
    
    if (status == update_ui.last_status and path_length == update_ui.last_path_length and 
        visited_count == update_ui.last_visited_count and queue_size == update_ui.last_queue_size):
        return

    update_ui.last_status = status
    update_ui.last_path_length = path_length
    update_ui.last_visited_count = visited_count
    update_ui.last_queue_size = queue_size

    font_size = 30
    font = pygame.font.Font(None, font_size)
    screen.fill(DEFAULT_NODE_COLOR, (0, WIDTH, WIDTH, 160))  # clear the UI area
    status_str = f"Status: {status}"
    path_length_str = f"Path Length: {path_length}"
    visited_count_str = f"Visited Nodes: {visited_count}"
    queue_size_str = f"Queue Size: {queue_size}"

    display_text(screen, status_str, (10, WIDTH + 20))
    display_text(screen, path_length_str, (10, WIDTH + 55))
    display_text(screen, visited_count_str, (10, WIDTH + 90))
    display_text(screen, queue_size_str, (10, WIDTH + 125))

    pygame.display.update((0, WIDTH, WIDTH, 160))  # only update the UI area

def main(algorithm, map_type):
    plan = get_algorithm(algorithm)
    if not plan:
        print("No valid planning algorithm found. Exiting.")
        return

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, WIDTH + 160))

    running = True
    usedPreviously = False

    grid, start, end = get_map(map_type)
    if not grid or not start or not end:
        print("No valid Canvas found. Exiting.")
        return

    status = "Idle"
    path_length = 0
    visited_count = 0
    queue_size = 0
    while running:
        draw(grid)
        update_ui(screen, status, path_length, visited_count, queue_size)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                node = grid[row][col]

                if not start and node != end and node.get_color() != BARRIER_COLOR:
                    node.set_color(START_COLOR)
                    start = node
                elif not end and node != start and node.get_color() != BARRIER_COLOR:
                    node.set_color(END_COLOR)
                    end = node
                elif node != end and node != start:
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
                    result = plan(lambda: draw(grid), lambda s, pl, vc, qs: update_ui(screen, s, pl, vc, qs), grid, start, end)
                    update_ui(screen,result[0],result[1],result[2],result[3])
                    usedPreviously = True
                    status, path_length, visited_count, queue_size = result
                elif event.key == pygame.K_c:
                    usedPreviously = False
                    end = None
                    reset(grid, keep_start=True)
                    grid, start, end = get_map(map_type)
                    status = "Canvas Reset"
                    visited_count = 0
                    queue_size = 0
                    path_length = 0
                elif event.key == pygame.K_d:
                    usedPreviously = False
                    start = None
                    end = None
                    reset(grid, all=True)
                    status = "Create your own map"
                    visited_count = 0
                    queue_size = 0
                    path_length = 0
                elif event.key == pygame.K_s:
                    save_map(grid)
                    print("Map saved as map.json")

    pygame.quit()

if __name__ == "__main__":
    args = get_args()
    main(args.algorithm, args.map)