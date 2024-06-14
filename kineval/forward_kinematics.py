from kineval import Robot, Link, Joint, Mat4D

# TODO: you may want to import other modules, such as numpy or scipy.spatial.transform

# FIXME: remove instructor imports
import numpy as np
from scipy.spatial.transform import Rotation as R


def TraverseRobotFK(robot: Robot):
    """Traverses the robot kinematic chain and sets the
    `transform` property of the robot and the joints.
    May call `tranverse_link_FK` and `traverse_joint_FK`.

    Args:
        robot (Robot): The robot to do forward kinematics on.
    """
    # TODO: YOUR CODE HERE

    # FIXME: remove instructor solution below
    mstack = np.identity(4)
    mstack[0:3, 0:3] = R.from_euler("XYZ", np.array(robot.rpy)).as_matrix()
    mstack[0:3, 3] = robot.xyz
    robot.transform = mstack
    TraverseLinkFK(mstack, robot.base)


def TraverseLinkFK(mstack: Mat4D, link: Link):
    """Helper function to traverse a link during FK.

    Args:
        mstack (Mat4D): Current transformation matrix on stack.
        link (Link): Link to traverse.
    """
    # TODO: YOUR CODE HERE

    # FIXME: remove instructor solution below
    for joint in link.children:
        TraverseJointFK(np.copy(mstack), joint)


def TraverseJointFK(mstack: Mat4D, joint: Joint):
    """Helper function to traverse a joint during FK.

    Args:
        mstack (Mat4D): Current transformation matrix on stack.
        joint (Joint): Joint to traverse.
    """
    # TODO: YOUR CODE HERE

    # FIXME: remove instructor solution below
    q = np.identity(4)
    quat = [*(np.sin(joint.theta / 2) * joint.axis), np.cos(joint.theta / 2)]
    q[0:3, 0:3] = R.from_quat(quat).as_matrix()

    m = np.identity(4)
    m[0:3, 0:3] = R.from_euler("XYZ", np.array(joint.rpy)).as_matrix()
    m[0:3, 3] = joint.xyz
    m = m @ q
    mstack = mstack @ m
    joint.transform = mstack
    TraverseLinkFK(mstack, joint.child)
