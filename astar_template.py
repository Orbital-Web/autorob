import numpy as np
from utils import get_collision_fn_PR2, load_env, execute_trajectory, draw_sphere_marker,draw_line
from pybullet_tools.utils import connect, disconnect, get_joint_positions, wait_if_gui, set_joint_positions, joint_from_name, get_link_pose, link_from_name
from pybullet_tools.pr2_utils import PR2_GROUPS
import time
### YOUR IMPORTS HERE ###
from queue import PriorityQueue
import math
EPSILON = 1e-5  
def is_close(a, b):
    return abs(a - b) < EPSILON

class Node:
    def __init__(self,x_in,y_in,theta_in):
        self.x = round(x_in, 5)
        self.y = round(y_in, 5)
        self.theta = round(theta_in, 5)

    def printme(self):
        print("\tNode"+ " x =", self.x, "y =",self.y, "theta =", self.theta)
    def __eq__(self, other):
        if isinstance(other, Node):
            return is_close(self.x, other.x) and is_close(self.y, other.y) and is_close(self.theta, other.theta)
        return False
    def __hash__(self):
        return hash((self.x, self.y, self.theta))

#########################
#cost function for node n and node m
def cost(n, m):
    d_theta = min(abs(n.theta - m.theta), 2*math.pi - abs(n.theta - m.theta))
    return math.sqrt((n.x - m.x)**2 + (n.y - m.y)**2 + d_theta**2)
#heuristic function 
def heuristic(n, goal):
    d_theta = min(abs(n.theta - goal.theta), 2*math.pi - abs(n.theta - goal.theta))
    return math.sqrt((n.x - goal.x)**2 + (n.y - goal.y)**2 + d_theta**2)
#get neighbors using own discretization of each degree of freedom 
DELTA_THETA=np.pi/2
DELTA_X=0.1 #goal /13
DELTA_Y=0.1 #goal /13
#global id counter
NODE_ID_COUNTER = 0
ID_Q_COUNTER=0
def generate_neighbors_4(node, collision_fn):
    global NODE_ID_COUNTER
    neighbors = []
    x, y, theta = node.x, node.y, node.theta
    
    # Define movement directions and their corresponding theta changes
    # Assuming: 0=East, pi/2=North, pi=West, -pi/2=South
    # These are relative changes based on the current theta
    deltas = [
        (DELTA_X, 0, 0),          # Move to the right, no relative theta change
        (-DELTA_X, 0, 0),         # Move to the left, no relative theta change
        (0, DELTA_Y, 0),          # Move upwards, no relative theta change
        (0, -DELTA_Y, 0),
        (0, 0, -DELTA_THETA),
        (0, 0, DELTA_THETA)          # Move downwards, no relative theta change
    ]

    for dx, dy, dtheta in deltas:
        new_x, new_y, new_theta = x + dx, y + dy, wrap_angle(theta + dtheta)
        if not collision_fn((new_x, new_y, new_theta)):
            neighbors.append(Node(new_x, new_y, new_theta))
        #else:
            #draw_node(new_x,new_y,color=(1, 0, 0, 1))
            
    
    NODE_ID_COUNTER += len(neighbors)
    return neighbors
def generate_neighbors_8(node, collision_fn):
    global NODE_ID_COUNTER
    neighbors = []
    x, y, theta = node.x, node.y, node.theta
    deltas = [(DELTA_X, 0), (-DELTA_X, 0), (0, DELTA_Y), (0, -DELTA_Y), 
              (DELTA_X, DELTA_Y), (DELTA_X, -DELTA_Y), (-DELTA_X, DELTA_Y), (-DELTA_X, -DELTA_Y)]

    for dx, dy in deltas:
        new_x, new_y = x + dx, y + dy
        temp = (new_x, new_y, theta)
        if not collision_fn(temp):
            neighbors.append(Node(new_x, new_y, theta))
        #else:
            #draw_node(temp[0],temp[1],color=(1, 0, 0, 1))
    for i in range(int(2 * math.pi / DELTA_THETA)):
        rotated_theta = wrap_angle(theta + i * DELTA_THETA)
        temp = (x, y, rotated_theta)
        if not collision_fn(temp):
            neighbors.append(Node(x, y, rotated_theta))
        #else:
            #draw_node(temp[0],temp[1],color=(1, 0, 0, 1))
    NODE_ID_COUNTER += len(neighbors)
    return neighbors

def draw_node(x,y, color):
    return
    # Drawing nodes slightly above the floor to ensure visibility
    #draw_sphere_marker((x, y, 0.05), 0.05, color)

# def generate_neighbors_8(node,id):
#     x, y, theta,parentid_in = node.x, node.y, node.theta,node.id
#     id1=id+1
#     id2=id+2
#     id3=id+3
#     id4=id+4
#     id5=id+5
#     id6=id+6
#     id7=id+7
#     id8=id+8
#     id9=id+9
#     id10=id+10
#     neighbors = [
#         Node(x + DELTA_X, y, theta, id1, parentid_in),
#         Node(x - DELTA_X, y, theta, id2, parentid_in),
#         Node(x, y + DELTA_Y, theta, id3, parentid_in),
#         Node(x, y - DELTA_Y, theta, id4, parentid_in),
#         Node(x + DELTA_X, y + DELTA_Y, theta, id5, parentid_in),
#         Node(x - DELTA_X, y - DELTA_Y, theta, id6, parentid_in),
#         Node(x + DELTA_X, y - DELTA_Y, theta, id7, parentid_in),
#         Node(x - DELTA_X, y + DELTA_Y, theta, id8, parentid_in),
#         Node(x, y, wrap_angle(theta + DELTA_THETA), id9, parentid_in),
#         Node(x, y, wrap_angle(theta - DELTA_THETA), id10, parentid_in),
#     ]

#     return neighbors,id10 
def wrap_angle(theta):
    while theta <= -math.pi:
        theta += 2 * math.pi
    while theta > math.pi:
        theta -= 2 * math.pi
    return theta
def main(screenshot=False):

    # initialize PyBullet
    connect(use_gui=True)
    # load robot and obstacle resources
    robots, obstacles = load_env('pr2doorway.json')

    # define active DoFs
    base_joints = [joint_from_name(robots['pr2'], name) for name in PR2_GROUPS['base']]

    collision_fn = get_collision_fn_PR2(robots['pr2'], base_joints, list(obstacles.values()))
    # Example use of collision checking
    # print("Robot colliding? ", collision_fn((0.5, -1.3, -np.pi/2)))

    # Example use of setting body poses
    # set_pose(obstacles['ikeatable6'], ((0, 0, 0), (1, 0, 0, 0)))

    # Example of draw 
    # draw_sphere_marker((0, 0, 1), 0.1, (1, 0, 0, 1))
    
    start_config = tuple(get_joint_positions(robots['pr2'], base_joints))
    goal_config = (2.6, -1.3, -np.pi/2)
    path = []
    start_time = time.time()
    ### YOUR CODE HERE ###
    #run a star algorithm
    path =Eight_Connect_Astar(start_config, goal_config,path,collision_fn)
    if path is None:
        print("No Solution Found.")
        return
    ######################
    print("Planner run time: ", time.time() - start_time)
    # Execute planned path
    execute_trajectory(robots['pr2'], base_joints, path, sleep=0.2)
    # Keep graphics window opened
    wait_if_gui()
    disconnect()

def is_close_enough(node, goal):
    return is_close(node.x, goal.x) and is_close(node.y, goal.y) and is_close(node.theta, goal.theta)
def Four_Connect_Astar(start_config,goal_config,path,collision_fn):
    #initialize start point and goal
    id=0
    global ID_Q_COUNTER
    x,y,theta=start_config[0],start_config[1],start_config[2]
    start=Node(x,y,theta)
    goal=Node(goal_config[0],goal_config[1],goal_config[2])
    open_list=PriorityQueue() #search queue
    open_set=set()
    closed_set=set()
    open_set.add(start)
    g_scores = {start: 0}
    parent_map = {}
    #put start point into pq
    open_list.put((0,0,start))
    #loop for search path
    while(not open_list.empty()):
        _,_,current_node=open_list.get()
        #draw_node(current_node.x,current_node.y,color=(0, 0, 1, 1))
        open_set.remove(current_node)
        print("current node\n")
        current_node.printme()
        #print("id_q2\n")
        #print(id_q)
        #TO DO sometimes not complete equal
        if is_close_enough(current_node, goal):
            print("success")
            return reconstruct_path(parent_map, current_node)
        closed_set.add(current_node)
        neighbors= generate_neighbors_4(current_node,collision_fn)
        #print("success create neighbors")
        for neighbor in neighbors:
            #print(neighbor.id)
            # if neighbor in closed_set and (neighbor not in g_scores or tentative_g_score >= g_scores[neighbor]):
            #     print("visited")
            #     continue
            # if collision_fn((neighbor.x, neighbor.y, neighbor.theta)):
            #     print("collide!")
            #     closed_set.add(neighbor)
            #     continue
            # tentative_g_score = g_scores[current_node] + cost(current_node, neighbor)
            # if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
            #     g_scores[neighbor] = tentative_g_score
            #     priority = tentative_g_score + heuristic(neighbor, goal)
            #     open_list.put((priority, ID_Q_COUNTER, neighbor))
            #     ID_Q_COUNTER += 1
            #     parent_map[neighbor] = current_node
                #print("pass collide")
            
            
            
            if(neighbor not in closed_set and neighbor not in open_set):
                #print("not in closed_set")
                tentative_g_score = g_scores[current_node] + cost(current_node, neighbor)
                if((neighbor not in g_scores or g_scores[neighbor]>tentative_g_score)and neighbor not in open_set):
                    g_scores[neighbor] = tentative_g_score
                    priority = tentative_g_score + heuristic(neighbor, goal)
                    open_list.put((priority, ID_Q_COUNTER, neighbor))
                    ID_Q_COUNTER += 1
                    parent_map[neighbor] = current_node
                    open_set.add(neighbor)
                    

            #if neighbor not in 

    return None
def reconstruct_path(parent_map, current_node):
    path = []
    while current_node is not None:
        path.append((current_node.x, current_node.y, current_node.theta))
        parent = parent_map.get(current_node)
        if parent:
            draw_line((parent.x, parent.y, 0.2), (current_node.x, current_node.y, 0.2), 2, (0, 0, 0))  # Drawing in green, thicker line.
            #draw_line(prev_pose[0],ee_pose[0],5,(255,0,0))
        current_node = parent
    return path[::-1]

def Eight_Connect_Astar(start_config,goal_config,path,collision_fn):
    id=0
    global ID_Q_COUNTER
    x,y,theta=start_config[0],start_config[1],start_config[2]
    start=Node(x,y,theta)
    goal=Node(goal_config[0],goal_config[1],goal_config[2])
    open_list=PriorityQueue() #search queue
    open_set=set()
    closed_set=set()
    open_set.add(start)
    g_scores = {start: 0}
    parent_map = {}
    open_list.put((0,0,start))
    while(not open_list.empty()):
        _,_,current_node=open_list.get()
        #draw_node(current_node.x,current_node.y,color=(0, 0, 1, 1))
        open_set.remove(current_node)
        print("current node\n")
        current_node.printme()
        if is_close_enough(current_node, goal):
            print("success")
            return reconstruct_path(parent_map, current_node)
        closed_set.add(current_node)
        neighbors= generate_neighbors_8(current_node,collision_fn)
        for neighbor in neighbors:
            if(neighbor not in closed_set and neighbor not in open_set):
                tentative_g_score = g_scores[current_node] + cost(current_node, neighbor)
                if((neighbor not in g_scores or g_scores[neighbor]>tentative_g_score)and neighbor not in open_set):
                    g_scores[neighbor] = tentative_g_score
                    priority = tentative_g_score + heuristic(neighbor, goal)
                    open_list.put((priority, ID_Q_COUNTER, neighbor))
                    ID_Q_COUNTER += 1
                    parent_map[neighbor] = current_node
                    open_set.add(neighbor)
                    

            #if neighbor not in 

    return None

if __name__ == '__main__':
    main()
