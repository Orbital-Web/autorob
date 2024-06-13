import os
import numpy as np
#TODO temp sol 
current_directory = os.path.dirname(os.path.abspath(__file__))
direct1_directory = os.path.abspath(os.path.join(current_directory, '..', '..'))
os.sys.path.insert(0, direct1_directory)
from utils import load_env, get_collision_fn_PR2, execute_trajectory, draw_sphere_marker, draw_line
from pybullet_tools.utils import connect, disconnect, wait_if_gui, wait_for_user, joint_from_name, get_joint_info, get_link_pose, link_from_name
from forward_kinematic_implementaiton import RobotKinematics
import pybullet as p

def main(screenshot=False):
    # initialize PyBullet
    connect(use_gui=True)
    
    # load robot and obstacle resources
    robots, obstacles = load_env('FK_env.json')
    
    # get the index for MR2
    MR2 = robots['mr2']

    # define example joint value
    joint_angles = [0, 0, 0, 0.0, np.pi/4, np.pi/2, np.pi/3, np.pi/6]

    # assign angle to joints
    for i, angle in enumerate(joint_angles):
        p.resetJointState(MR2, i, angle)

    # use student FK implementation
    robot_kin = RobotKinematics(MR2)

    # get the end-effector state using PyBullet
    end_effector_link_name = 'forearm_right'
    end_effector_index = link_from_name(MR2, end_effector_link_name)
    print("end effector index is", end_effector_index)
    link_state = p.getLinkState(MR2, end_effector_index)
    pybullet_position = np.array(link_state[4])
    pybullet_orientation = np.array(p.getMatrixFromQuaternion(link_state[5])).reshape(3, 3)

    # compute FK using your custom implementation
    robot_kin.build_fk_transforms(joint_angles)
    custom_fk_transform = robot_kin.end_effector_transform

    # extract position and orientation from the custom FK result
    custom_fk_position = custom_fk_transform[:3, 3]
    custom_fk_orientation = custom_fk_transform[:3, :3]

    # compare the results to check implementation
    position_difference = np.linalg.norm(pybullet_position - custom_fk_position)
    orientation_difference = np.linalg.norm(pybullet_orientation - custom_fk_orientation)

    print("PyBullet Position:", pybullet_position)
    print("Custom FK Position:", custom_fk_position)
    print("Position Difference:", position_difference)

    print("PyBullet Orientation:\n", pybullet_orientation)
    print("Custom FK Orientation:\n", custom_fk_orientation)
    print("Orientation Difference:", orientation_difference)

    # keep graphics window opened
    wait_for_user()
    wait_if_gui()
    disconnect()

if __name__ == '__main__':
    main()