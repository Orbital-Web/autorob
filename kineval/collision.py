from kineval import Robot, World, Link, Joint, Vec2, Mat4

# TODO: you may want to import other modules, such as numpy or scipy.spatial.transform

# FIXME: remove instructor imports
import numpy as np
from scipy.spatial.transform import Rotation as R


class RobotConfiguration:
    """A class for storing the configuration of the robot."""

    def __init__(self, robot: Robot):
        """Builds the current configuration for the robot.

        Args:
            robot (Robot): Robot to build the configuration from.
        """
        self.base_position: Vec2 = robot.xyz[:2]  # xy position of base
        self.base_config: float = robot.rpy[2]  # z axis rotation of base
        self.joint_configs: dict[str, float] = {
            joint.name: joint.theta for joint in robot.joints
        }  # mapping of joint name to joint theta


def IsCollision(robot: Robot, world: World) -> bool:
    """Returns whether the robot is currently in collision.

    Args:
        robot (Robot): Robot to check collision for.
        world (World): World the robot is in.

    Returns:
        bool: Whether the robot is in collision.
    """
    configuration = RobotConfiguration(robot)  # get current configuration
    return IsPoseCollison(robot, configuration, world)


def IsPoseCollison(
    robot: Robot, configuration: RobotConfiguration, world: World
) -> bool:
    """Returns whether the robot in the given configuration is
    in collision.
    May call `CollisionLinkFK` and `CollisionJointFK`.

    Args:
        robot (Robot): Robot to check collision for.
        configuration (RobotConfiguration): Configuration to check against.
        world (World): World the robot is in.

    Returns:
        bool: Whether the robot is in collision.
    """
    # NOTE: This function is already written for you

    # check whether center of base is within bounds of the world
    robot_x, robot_y = configuration.base_position
    if (
        robot_x < world.bounds[0][0]
        or robot_x > world.bounds[0][1]
        or robot_y < world.bounds[1][0]
        or robot_y > world.bounds[1][1]
    ):
        return True

    # TODO: YOUR CODE HERE
    # Build the base mstack and resursively call `CollisionLinkFK` and `CollisionJointFK`
    # DO NOT modify any part of the robot when traversing

    # FIXME: remove instructor solution below
    mstack = np.identity(4)
    mstack[0:3, 0:3] = R.from_euler("Z", configuration.base_config).as_matrix()
    mstack[0:2, 3] = configuration.base_position
    return CollisionLinkFK(mstack, robot.base, configuration, world)


def CollisionJointFK(
    mstack: Mat4, joint: Joint, configuration: RobotConfiguration, world: World
) -> bool:
    """Checks whether the joint's descendants are in collision.
    Updates mstack and calls `CollisionLinkFK` for the child link.

    Args:
        mstack (Mat4): Current transformation matrix on stack.
        joint (Joint): Joint to traverse.
        configuration (RobotConfiguration): Configuration to check against.
        world (World): World the robot is in.

    Returns:
        bool: Whether the joint's descendants are in collision.
    """
    # TODO: YOUR CODE HERE
    # Update the mstack and call `CollisionLinkFK` for the child link
    # DO NOT modify any part of the robot when traversing

    # FIXME: remove instructor solution below
    m = np.identity(4)
    m[0:3, 0:3] = R.from_euler("XYZ", np.array(joint.rpy)).as_matrix()
    m[0:3, 3] = joint.xyz

    # apply joint configuration
    q = np.identity(4)
    if joint.type == Joint.JointType.PRISMATIC:
        m[0:3, 3] += joint.axis * joint.theta
    else:
        quat = [*(np.sin(joint.theta / 2) * joint.axis), np.cos(joint.theta / 2)]
        q[0:3, 0:3] = R.from_quat(quat).as_matrix()
    m = m @ q

    mstack = mstack @ m
    return CollisionLinkFK(mstack, joint.child, configuration, world)


def CollisionLinkFK(
    mstack: Mat4, link: Link, configuration: RobotConfiguration, world: World
) -> bool:
    """Checks whether the link or its descendants are in collision.
    Calls `CollisionJointFK` for the children joints.

    Args:
        mstack (Mat4): Current transformation matrix on stack.
        link (Link): Link to traverse.
        configuration (RobotConfiguration): Configuration to check against.
        world (World): World the robot is in.

    Returns:
        bool: Whether the link or its descendants are in collision.
    """
    # NOTE: This function is already written for you

    # check collision of this link

    # recurse to child joints
    for joint in link.children:
        collided = CollisionJointFK(np.copy(mstack), joint, configuration, world)
        if collided:
            return True

    # no collision in any of its descendants
    return False
