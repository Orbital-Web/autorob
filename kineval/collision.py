from kineval import Robot, World, Link, Joint, Vec, Vec2, Mat4

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
        self.base_position: Vec2 = np.array(robot.xyz[:2], float)  # xy position of base
        self.base_rotation: float = robot.rpy[2]  # z axis rotation of base
        self.joint_configs: dict[str, float] = {
            joint.name: joint.theta for joint in robot.joints
        }  # mapping of joint name to joint theta

    def fromVec(self, vector: Vec):
        """Initializes the RobotConfiguration from a vector.
        Index 0 and 1 is for the robot base position, while index 2 is
        for the robot base rotation. Remaining indices are used for the
        joint configurations, in the order of robot.joints.

        Args:
            vector (Vec): Input vector to initialize with.
        """
        expected = 3 + len(self.joint_configs)
        if len(vector) != expected:
            raise ValueError(f"Invalid input vector. Expected a length of {expected}.")
        self.base_position = np.array(vector[:2])
        self.base_rotation = vector[2]
        for i, joint_name in enumerate(self.joint_configs):
            self.joint_configs[joint_name] = vector[i + 2]

    def asVec(self) -> Vec:
        """Returns the vector representation of the RobotConfiguration.
        Index 0 and 1 is for the robot base position, while index 2 is
        for the robot base rotation. Remaining indices are used for the
        joint configurations, in the order of robot.joints.

        Returns:
            Vec: The vector representation of the configuration.
        """
        vector = [*self.base_position, self.base_rotation]
        for joint_theta in self.joint_configs.values():
            vector.append(joint_theta)
        return np.array(vector, float)


def IsCollision(robot: Robot, world: World) -> bool:
    """Returns whether the robot is currently in collision.

    Args:
        robot (Robot): Robot to check collision for.
        world (World): World the robot is in.

    Returns:
        bool: Whether the robot is in collision.
    """
    # NOTE: This function is already written for you
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
    # check whether center of base is within bounds of the world
    robot_x, robot_y = configuration.base_position
    if (
        robot_x < world.bounds[0][0]
        or robot_x > world.bounds[0][1]
        or robot_y < world.bounds[1][0]
        or robot_y > world.bounds[1][1]
    ):
        robot.base.bbox_geom.SetVisibility(True)
        return True
    robot.base.bbox_geom.SetVisibility(False)

    # TODO: YOUR CODE HERE
    # Finish the rest of the function by building the base mstack and resursively
    # callin `CollisionLinkFK` and `CollisionJointFK`
    # DO NOT modify any part of the robot when traversing

    # FIXME: remove instructor solution below
    mstack = np.identity(4)
    mstack[0:3, 0:3] = R.from_euler("Z", configuration.base_rotation).as_matrix()
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
    inverse_transform = np.linalg.inv(mstack)
    for obstacle in world.obstacles:
        # transform obstacle origin to link frame
        origin_local = (inverse_transform @ obstacle.origin_homogeneous)[:3]
        # find closest point on box to obstacle
        closest = np.clip(origin_local, link.bbox[::2], link.bbox[1::2])
        # check if distance is less than radius (in collision)
        if np.linalg.norm(closest - origin_local) <= obstacle.radius:
            link.bbox_geom.SetVisibility(True)
            return True
        # not in collision
        link.bbox_geom.SetVisibility(False)

    # recurse to child joints
    for joint in link.children:
        if CollisionJointFK(np.copy(mstack), joint, configuration, world):
            return True

    # no collision in any of its descendants
    return False
