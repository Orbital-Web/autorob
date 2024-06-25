from kineval import Robot, Link, Joint, Mat4

# TODO: you may want to import other modules, such as numpy or scipy.spatial.transform

# FIXME: remove instructor imports
import numpy as np
from scipy.spatial.transform import Rotation as R


def TraverseRobotFK(robot: Robot):
    """Traverses the robot kinematic chain and sets the `transform` property of the
    robot and the joints. May call `TraverseLinkFK` and `TraverseJointFK`.

    Args:
        robot (Robot): The robot to do forward kinematics on.
    """
    # TODO: YOUR CODE HERE
    # Build the base mstack and recursively call `TraverseLinkFK` and `TraverseJointFK`

    # FIXME: remove instructor solution below
    mstack = np.identity(4)
    mstack[0:3, 0:3] = R.from_euler("XYZ", np.array(robot.rpy)).as_matrix()
    mstack[0:3, 3] = robot.xyz
    robot.transform = mstack
    TraverseLinkFK(mstack, robot.base)


def TraverseLinkFK(mstack: Mat4, link: Link):
    """Helper function to traverse a link during FK.

    Args:
        mstack (Mat4D): Current transformation matrix on stack.
        link (Link): Link to traverse.
    """
    # TODO: YOUR CODE HERE
    # Call `TraverseJointFK` for the child joints

    # FIXME: remove instructor solution below
    for joint in link.children:
        TraverseJointFK(np.copy(mstack), joint)


def TraverseJointFK(mstack: Mat4, joint: Joint):
    """Helper function to traverse a joint during FK. May call `ApplyJointLimits`.

    Args:
        mstack (Mat4D): Current transformation matrix on stack.
        joint (Joint): Joint to traverse.
    """
    # TODO: YOUR CODE HERE
    # Update the mstack and call `TraverseLinkFK` for the child link

    # FIXME: remove instructor solution below
    m = np.identity(4)
    m[0:3, 0:3] = R.from_euler("XYZ", np.array(joint.rpy)).as_matrix()
    m[0:3, 3] = joint.xyz

    # apply joint configuration
    ApplyJointLimits(joint)
    q = np.identity(4)
    if joint.type == Joint.JointType.PRISMATIC:
        m[0:3, 3] += joint.axis * joint.theta
    else:
        quat = [*(np.sin(joint.theta / 2) * joint.axis), np.cos(joint.theta / 2)]
        q[0:3, 0:3] = R.from_quat(quat).as_matrix()
    m = m @ q

    mstack = mstack @ m
    joint.transform = mstack
    TraverseLinkFK(mstack, joint.child)


def ApplyJointLimits(joint: Joint):
    """Ensures the joint theta does not exceed it joint limits. If `joint.limits` is
    None, the joint does not have a joint limit. Otherwise, ensure `joint.theta` is
    within `joint.limits[0]` and `joint.limits[1]`.

    Args:
        joint (Joint): The joint to apply joint limits.
    """
    # TODO: YOUR CODE HERE
    # Clamp `joint.theta` within the joint limits

    # FIXME: remove instructor solution below
    if not joint.limits:
        return
    lower, upper = joint.limits
    joint.theta = max(lower, min(upper, joint.theta))
