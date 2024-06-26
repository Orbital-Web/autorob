from infrastructure import GRID_COLOR,DEFAULT_NODE_COLOR,BARRIER_COLOR,CLOSED_COLOR ,END_COLOR,PATH_COLOR,START_COLOR,OPEN_COLOR 
from queue import PriorityQueue
import math
import pygame

from infrastructure import GRID_COLOR, DEFAULT_NODE_COLOR, BARRIER_COLOR, CLOSED_COLOR, END_COLOR, PATH_COLOR, START_COLOR, OPEN_COLOR
from queue import PriorityQueue
import math
import pygame

def astar_algorithm(draw, update_ui, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    open_set_hash = {start}

    came_from = {}
    g_score = {node: float('inf') for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float('inf') for row in grid for node in row}
    f_score[start] = dist(start.get_pos(), end.get_pos())

    visited_count = 0
    queue_size = 1
    status = "Iterating"

    last_status = ""
    last_path_length = 0
    last_visited_count = 0
    last_queue_size = 0

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "Quit", 0, visited_count, queue_size

        current = open_set.get()[2]
        open_set_hash.remove(current)
        visited_count += 1

        if current == end:
            path_length = reconstruct_path(came_from, current, start, end, draw)
            end.set_color(END_COLOR)  # Reset end color after all processing
            return "Success", path_length, visited_count, queue_size

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + dist(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor != end:  # Avoid changing the end node's color
                        neighbor.set_color(OPEN_COLOR)

        draw()

        if status != last_status or visited_count != last_visited_count or len(open_set_hash) != last_queue_size:
            last_status = status
            last_path_length = 0
            last_visited_count = visited_count
            last_queue_size = len(open_set_hash)
            update_ui(status, 0, visited_count, len(open_set_hash))

        if current != start and current != end:
            current.set_color(CLOSED_COLOR)

    return "Failure", 0, visited_count, queue_size

def dist(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def reconstruct_path(came_from, current, start, end, draw):
    path_length = 0
    while current in came_from:
        next_node = came_from[current]
        if current != start and current != end:
            current.set_color(PATH_COLOR)
        draw()
        path_length += dist((current.x, current.y), (next_node.x, next_node.y))
        current = next_node

    if current != start and current != end:
        current.set_color(PATH_COLOR)
        draw()

    return path_length