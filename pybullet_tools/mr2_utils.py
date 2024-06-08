# Credits
# This file is adapted from Open Source projects. You can find the source code of their open source projects
# below. We acknowledgde and are gradteful to these contributors for their contributions.
# 
# Caelan Reed Garrett. PyBullet Planning. https://pypi.org/project/pybullet-planning/. 2020.
# Modified for mr2
import math
import os
import random
import re
from collections import namedtuple
from itertools import combinations

import numpy as np

from .mr2_never_collisions import NEVER_COLLISIONS
from .utils import get_link_pose, set_joint_position, set_joint_positions, get_joint_positions, get_min_limit, get_max_limit,\
    link_from_name, Pose, joints_from_names, get_body_name, get_num_joints, Euler, get_links, get_link_name, PI

# constants


#####################################

MR2_GROUPS = {
    'base': ['x','y','theta'],
    #'base': ['clavicle_right_yaw'],
    # 'base': ['shoulder_right_yaw'],
    # 'base': ['upperarm_right_pitch'],
    # 'base': ['forearm_right_yaw'],
    # 'base': ['clavicle_left_roll'] 
}


MR2_BASE_LINK = 'base'

TOOL_POSE = Pose(euler=Euler(pitch=np.pi/2))


#####################################

# MR2_URDF = "models/drake/mr2_description/urdf/mr2.urdf"
MR2_URDF = "models/drake/pr2_description/urdf/mr2.urdf"

#####################################

def get_base_pose(mr2):
    return get_link_pose(mr2, link_from_name(mr2, MR2_BASE_LINK))

#####################################

def get_disabled_collisions(mr2):
    disabled_names = NEVER_COLLISIONS
    link_mapping = {get_link_name(mr2, link): link for link in get_links(mr2)}
    return {(link_mapping[name1], link_mapping[name2])
            for name1, name2 in disabled_names if (name1 in link_mapping) and (name2 in link_mapping)}

#####################################

def get_groups():
    return sorted(MR2_GROUPS)

def get_group_joints(robot, group):
    return joints_from_names(robot, MR2_GROUPS[group])

def get_group_conf(robot, group):
    return get_joint_positions(robot, get_group_joints(robot, group))

def set_mr2_group_conf(robot, group, positions):
    #get_group_joints return related group joints
    set_joint_positions(robot, get_group_joints(robot, group), positions)

def set_group_positions(robot, group_positions):
    for group, positions in group_positions.items():
        set_mr2_group_conf(robot, group, positions)

def get_group_positions(robot):
    return {group: get_group_conf(robot, group) for group in get_groups()}

#####################################

