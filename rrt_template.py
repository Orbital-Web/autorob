import numpy as np
from utils import load_env, get_collision_fn_PR2, execute_trajectory
from pybullet_tools.utils import connect, disconnect, wait_if_gui, joint_from_name, get_joint_positions, set_joint_positions, get_joint_info, get_link_pose, link_from_name
import random
### YOUR IMPORTS HERE ###
import time
import math
from utils import draw_sphere_marker,draw_line
#########################
#Tree Node
class Node:
    def __init__(self,configuration):
        self.config = configuration #x,y,z,orientation
        self.parent = None
        self.children = []
    def add_child(self, child_node):
        self.children.append(child_node)
        child_node.parent = self
    def printme(self):
        print("\tNode: configuration ",self.config)
class RRTree:
    def __init__(self, start_config):
        self.root = Node(start_config)
        self.nodes = [self.root]

    def add_node(self, parent_node,configuration):
        new_node = Node(configuration)
        parent_node.add_child(new_node)
        self.nodes.append(new_node)
        return new_node

joint_names =('l_shoulder_pan_joint','l_shoulder_lift_joint','l_elbow_flex_joint','l_upper_arm_roll_joint','l_forearm_roll_joint','l_wrist_flex_joint')
def draw_node_start(config, color=(0, 1, 0, 1)):  # green color
    draw_sphere_marker((config[0], config[1], config[2]), 0.02, color)

# Function to draw the goal node in purple
def draw_node_goal(config, color=(0.5, 0, 0.5, 1)):  # purple color
    draw_sphere_marker((config[0], config[1], config[2]), 0.02, color)
def main(screenshot=False):
    # initialize PyBullet
    connect(use_gui=True)
    # load robot and obstacle resources
    robots, obstacles = load_env('pr2table.json')

    # define active DoFs
    joint_names =('l_shoulder_pan_joint','l_shoulder_lift_joint','l_elbow_flex_joint','l_upper_arm_roll_joint','l_forearm_roll_joint','l_wrist_flex_joint')
    joint_idx = [joint_from_name(robots['pr2'], jn) for jn in joint_names]

    # parse active DoF joint limitsd
    joint_limits = {joint_names[i] : (get_joint_info(robots['pr2'], joint_idx[i]).jointLowerLimit, get_joint_info(robots['pr2'], joint_idx[i]).jointUpperLimit) for i in range(len(joint_idx))}
    collision_fn = get_collision_fn_PR2(robots['pr2'], joint_idx, list(obstacles.values()))
    # Example use of collision checking
    # print("Robot colliding? ", collision_fn((0.5, 1.19, -1.548, 1.557, -1.32, -0.1928)))

    start_config = tuple(get_joint_positions(robots['pr2'], joint_idx))
    goal_config = (0.5, 0.33, -1.548, 1.557, -1.32, -0.1928)
    path=[]
    ### YOUR CODE HERE ###
    #change joint limit
    joint_limits['l_forearm_roll_joint']=(-math.pi,math.pi)
    start_time = time.time()
    path=RRT(start_config,K,STEP_SIZE,goal_config,joint_limits,collision_fn)
    print("Planner run time: ", time.time() - start_time)
    if path == None:
        print("No Solution Found.")
        return 
    else:
        PR2 = robots['pr2']  
        link_id = link_from_name(PR2, 'l_gripper_tool_frame')
        #print("smoothing working")
        path = ShortcutSmoothing(path, 150,collision_fn)
        #print("smoothed_path",smoothed_path)
        # prev_pose=None
        # for path1 in path:
        #     set_joint_positions(PR2, joint_idx, path1)  
        #     ee_pose = get_link_pose(PR2, link_id)
        #     if(prev_pose):
        #         draw_line(prev_pose[0],ee_pose[0],5,(255,0,0))
        #     prev_pose=ee_pose
        # prev_pose2=None
        # for path2 in smoothed_path:
        #     set_joint_positions(PR2, joint_idx, path2)  
        #     ee_pose = get_link_pose(PR2, link_id)
        #     draw_sphere_marker(ee_pose[0], 0.02, (0, 0, 1, 1))
        #     if(prev_pose2):
        #         draw_line(prev_pose2[0],ee_pose[0],5,(0,0,255))
        #     prev_pose2=ee_pose
   
    ######################
    # Execute planned path
    #####################
    execute_trajectory(robots['pr2'], joint_idx, path, sleep=0.1)
    ####################
    # Keep graphics window opened
    wait_if_gui()
    disconnect()
    #hard code path
    

STEP_SIZE=0.05
K=20000
#draw line
def draw_path(path,sm):
    t=len(path)-1
    p=0
    for i in range(t):
        line_start=(path[p][0],path[p][1],path[p][2])
        #print("line start", line_start)
        line_end=(path[p+1][0],path[p+1][1],path[p+1][2])
        #print("line end", line_end)
        line_width=20
        line_color=(255,0,0) #red 
        if sm:
            line_color=(0,0,255) #blue
        draw_line(line_start, line_end, line_width, line_color)
        p=p+1


#random generate new configuration

def random_configuration(joint_limits,goal,goal_bias=0.1):
    if(random.random()<=goal_bias):
        #print("selecting goal")
        #print('goal is', goal)
        return goal
    joint_names = list(joint_limits.keys())
    config =[]

    for joint in joint_names:
        lower_limit, upper_limit = joint_limits[joint]
        config.append(random.uniform(lower_limit, upper_limit))
    #print("random genertae config:",tuple(config))
    #draw_node_rand(tuple(config))
    return tuple(config)
#calculate distance between two configuration
def distance(config1, config2):
    distance=np.linalg.norm(np.array(config1)-np.array(config2))
    return distance
#iterate tree to find nearest node
def nearest_node(T, qrand):
    min_distance = float('inf')
    nearest = None
    for node in T.nodes:
        current_distance = distance(node.config, qrand)
        if current_distance < min_distance:
            min_distance = current_distance
            nearest = node 
    #print("nearest node is") 
    #nearest.printme()
    return nearest
#generate new configuration through RRTconnect
def new_configuration(q_near, q_rand, STEP_SIZE):
    q_near = list(q_near)
    q_rand = list(q_rand)
    direction = [qr - qn for qr, qn in zip(q_rand, q_near)]
    magnitude = sum(d**2 for d in direction)**0.5
    if magnitude == 0:
        #print("magnitidue equal to zero")
        return tuple(q_near)
    normalized_direction = [d/magnitude for d in direction]
    step = [d*STEP_SIZE for d in normalized_direction]
    q_new_list = [qn + s for qn, s in zip(q_near, step)]
    q_new = tuple(q_new_list)
    return q_new

#estimate the final step
def isclose_to(q_new,goal):
    q_new = np.array(q_new)
    goal = np.array(goal)
    if(np.linalg.norm(q_new-goal)<=STEP_SIZE):
        return True
    return False

#construct the path 
def construct_path(goal_node):
    path = []
    current_node = goal_node
    path.append(current_node.config)
    while current_node.parent:
        path.insert(0, current_node.config)
        current_node = current_node.parent
    return path
def interpolate(point1, point2,t):
    return tuple(p1+t*(p2-p1) for p1,p2 in zip(point1,point2))
    return q_new

def obstacle_between(q_near, q_new,collision_fn):
    if collision_fn(q_near) or collision_fn(q_new):

        return True
    return False

def RRT(start,K,STEP_SIZE,goal,joint_limits,collision_fn):
    T = RRTree(start)
    for i in range(K):
        print("iteration i: ", i)
        q_rand = random_configuration(joint_limits,goal)
        q_near = nearest_node(T, q_rand)
        #print("selecting new near because new rand")    

        while True:
            q_new = new_configuration(q_near.config, q_rand, STEP_SIZE)

            if (isclose_to(q_new, q_rand) and (q_rand!=goal)):
                #print("q_new reached q_rand, choosing a new road.")
                break  # break from the inner loop to choose a new q_rand
            #create failure check???
            collide=obstacle_between(q_near.config, q_new, collision_fn)
            if not collide:
                #print("qnear is")
                #q_near.printme()
                q_near = T.add_node(q_near, q_new)
                #print("continue selecting in line")
                #print("qnew is")
                #print(q_new)
                if isclose_to(q_near.config, goal):
                    #print("success")
                    return construct_path(q_near)
             
            else:
                #print("give up this line")
                break

    return None
def draw_node_new(node, color=(1, 0, 0, 1)): #red
    draw_sphere_marker((node[0], node[1], node[2]), 0.02, color)
def draw_node_rand(config, color=(0, 0, 1, 1)):#blue
    draw_sphere_marker((config[0], config[1], config[2]), 0.02, color)
def draw_node_near(node, color=(1, 1, 0, 1)): #yellow
    draw_sphere_marker((node.config[0], node.config[1], node.config[2]), 0.02, color)
def draw_node_red(node, color=(1, 0, 0, 1)):
    draw_sphere_marker((node[0], node[1], node[2]), 0.05, color)
def draw_node_red2(node, color=(1, 0, 0, 1)):
    draw_sphere_marker((node.config[0], node.config[1], node.config[2]), 0.02, color)
    
# Smoothing
def ShortcutSmoothing(path, iterations, collision_fn):
    for _ in range(iterations):
        i,j=sorted(random.sample(range(len(path)),2))
        if abs(i-j)<2:
            continue
        if is_valid(path[i],path[j],collision_fn):
            path=path[:i+1]+path[j:]
    return path
def is_valid(q1,q2,collision_fn):
    distance=sum((p2-p1)**2 for p1,p2 in zip(q1,q2))**0.5
    steps=int(distance/0.05)
    for i in range(steps):
        t=i/steps
        interplate_point=interpolate(q1,q2,t)
        if collision_fn(interplate_point):
            return False
    return True


if __name__ == '__main__':
    main()