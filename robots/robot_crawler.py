import math
from collections import defaultdict

##############################################################################################################################
# Not currently sure if it works out, but seems like to be doable.
##############################################################################################################################

# CREATE ROBOT STRUCTURE

# Define robot and links

# create robot data object
robot = {}

# give the robot a name
robot['name'] = "crawler"

# initialize start pose of robot in the world
robot['origin'] = {'xyz': [0, 1, 0], 'rpy': [0, 0, 0]}  # held a bit over the ground plane

# specify base link of the robot; robot.origin is transform of world to the robot base
robot['base'] = "base"

# specify and create data objects for the links of the robot
robot['links'] = {
    "base": {},
    "leg1_upper": {},
    "leg1_middle": {},
    "leg1_lower": {},
    "leg2_upper": {},
    "leg2_middle": {},
    "leg2_lower": {},
    "leg3_upper": {},
    "leg3_middle": {},
    "leg3_lower": {},
    "leg4_upper": {},
    "leg4_middle": {},
    "leg4_lower": {},
    "leg5_upper": {},
    "leg5_middle": {},
    "leg5_lower": {},
    "leg6_upper": {},
    "leg6_middle": {},
    "leg6_lower": {},
    "leg7_upper": {},
    "leg7_middle": {},
    "leg7_lower": {},
    "leg8_upper": {},
    "leg8_middle": {},
    "leg8_lower": {},
}

# specify name of endeffector frame
robot['endeffector'] = {'frame': "leg1_ankle", 'position': [[0], [0], [0.9], [1]]}

# Define joints and kinematic hierarchy

# specify and create data objects for the joints of the robot
robot['joints'] = {}

robot['joints']['leg1_hip'] = {'parent': "base", 'child': "leg1_upper", 'origin': {'xyz': [0.3, 0.0, 0.9], 'rpy': [0, math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg1_knee'] = {'parent': "leg1_upper", 'child': "leg1_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg1_ankle'] = {'parent': "leg1_middle", 'child': "leg1_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

robot['joints']['leg2_hip'] = {'parent': "base", 'child': "leg2_upper", 'origin': {'xyz': [0.3, 0.0, -0.9], 'rpy': [0, math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg2_knee'] = {'parent': "leg2_upper", 'child': "leg2_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg2_ankle'] = {'parent': "leg2_middle", 'child': "leg2_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

robot['joints']['leg3_hip'] = {'parent': "base", 'child': "leg3_upper", 'origin': {'xyz': [-0.3, 0.0, 0.9], 'rpy': [0, -math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg3_knee'] = {'parent': "leg3_upper", 'child': "leg3_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg3_ankle'] = {'parent': "leg3_middle", 'child': "leg3_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

robot['joints']['leg4_hip'] = {'parent': "base", 'child': "leg4_upper", 'origin': {'xyz': [-0.3, 0.0, -0.9], 'rpy': [0, -math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg4_knee'] = {'parent': "leg4_upper", 'child': "leg4_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg4_ankle'] = {'parent': "leg4_middle", 'child': "leg4_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

robot['joints']['leg5_hip'] = {'parent': "base", 'child': "leg5_upper", 'origin': {'xyz': [0.3, 0.0, 0.3], 'rpy': [0, math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg5_knee'] = {'parent': "leg5_upper", 'child': "leg5_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg5_ankle'] = {'parent': "leg5_middle", 'child': "leg5_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

robot['joints']['leg6_hip'] = {'parent': "base", 'child': "leg6_upper", 'origin': {'xyz': [0.3, 0.0, -0.3], 'rpy': [0, math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg6_knee'] = {'parent': "leg6_upper", 'child': "leg6_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg6_ankle'] = {'parent': "leg6_middle", 'child': "leg6_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

robot['joints']['leg7_hip'] = {'parent': "base", 'child': "leg7_upper", 'origin': {'xyz': [-0.3, 0.0, 0.3], 'rpy': [0, -math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg7_knee'] = {'parent': "leg7_upper", 'child': "leg7_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg7_ankle'] = {'parent': "leg7_middle", 'child': "leg7_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

robot['joints']['leg8_hip'] = {'parent': "base", 'child': "leg8_upper", 'origin': {'xyz': [-0.3, 0.0, -0.3], 'rpy': [0, -math.pi/2, 0]}, 'axis': [0.0, 1.0, 0.0]}
robot['joints']['leg8_knee'] = {'parent': "leg8_upper", 'child': "leg8_middle", 'origin': {'xyz': [0.0, 0.0, 0.4], 'rpy': [-math.pi/4, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}
robot['joints']['leg8_ankle'] = {'parent': "leg8_middle", 'child': "leg8_lower", 'origin': {'xyz': [0.0, 0.0, 0.6], 'rpy': [math.pi/2, 0, 0]}, 'axis': [1.0, 0.0, 0.0]}

# specify and create data objects for the materials of the robot
robot['materials'] = {
    "gray": {'color': [0.7, 0.7, 0.7, 1]},
    "red": {'color': [1, 0, 0, 1]},
    "green": {'color': [0, 1, 0, 1]},
    "blue": {'color': [0, 0, 1, 1]},
    "yellow": {'color': [1, 1, 0, 1]}
}
