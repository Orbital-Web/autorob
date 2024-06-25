from kineval import Robot, Joint, Vec3, Vec2, RobotConfiguration, RRTInfo
from scipy.spatial.transform import Rotation as R
import numpy as np


def MoveRobot(robot: Robot, direction: Vec2, speed: float):
    """Moves the robot in the specified direction. Increments `robot.xyz` by some vector
    v with magnitude `speed`, depending on `robot.facing` and `direction`.

    Args:
        robot (Robot): The robot to move.
        direction (Vec2): Move direction in +x and +y axis.
        speed (float): Speed of movement in m/tick.
    """
    up = np.array([0, 0, 1])  # up direction vector
    facing = robot.facing  # vector of forward direction
    lateral = np.cross(up, facing)  # vector of right direction

    # update robot position
    dxyz = direction[0] * speed * facing + direction[1] * speed * lateral
    robot.xyz += dxyz


def TurnRobot(robot: Robot, direction: float, speed: float):
    """Turns the robot in the specified direction.

    Args:
        robot (Robot): The robot to turn.
        direction (float): Turn direction. Clockwise when positive.
        speed (float): Speed of turning in rad/tick.
    """
    # only need to modify z axis rotation
    robot.rpy[2] -= direction * speed

    # update facing direction
    mstack = R.from_euler("XYZ", np.array(robot.rpy)).as_matrix()
    robot.facing = mstack @ np.array([1, 0, 0], float)


def TraverseJointUp(robot: Robot, color: Vec3, selected_color: Vec3):
    """Selects the next joint down the kinematic hierarchy.

    Args:
        robot (Robot): The robot to traverse.
        color (Vec3): Color of normal joint.
        selected_color (Vec3): Color of selected joint.
    """
    # select first child joint of child link
    if robot.selected.child.children:
        robot.selected.geom.prop.SetColor(*color)  # revert color
        robot.selected = robot.selected.child.children[0]
        robot.selected.geom.prop.SetColor(*selected_color)  # update color


def TraverseJointDown(robot: Robot, color: Vec3, selected_color: Vec3):
    """Selects the previous joint down the kinematic hierarchy.

    Args:
        robot (Robot): The robot to traverse.
        color (Vec3): Color of normal joint.
        selected_color (Vec3): Color of selected joint.
    """
    # select parent joint of parent link
    if robot.selected.parent.parent:
        robot.selected.geom.prop.SetColor(*color)  # revert color
        robot.selected = robot.selected.parent.parent
        robot.selected.geom.prop.SetColor(*selected_color)  # update color


def TraverseJointAdjacent(robot: Robot, color: Vec3, selected_color: Vec3):
    """Selects the adjacent joint of the same link.

    Args:
        robot (Robot): The robot to traverse.
        color (Vec3): Color of normal joint.
        selected_color (Vec3): Color of selected joint.
    """
    # ignore if link only has one children
    child_joints = robot.selected.parent.children
    n_children = len(child_joints)
    if n_children <= 1:
        return

    # find joint
    for i, joint in enumerate(child_joints):
        if joint == robot.selected:
            break
    # go to next joint (or wrap to first joint)
    robot.selected.geom.prop.SetColor(*color)  # revert color
    robot.selected = child_joints[(i + 1) % n_children]
    robot.selected.geom.prop.SetColor(*selected_color)  # update color


def ApplyControl(robot: Robot, direction: float, speed: float):
    """Modifies the robot's selected joint's theta in the specified direction. Turns the
    robot's selected joint if the joint is continuous or revolute. Extends or retracts
    the joint if the joint is prismatic.

    Args:
        robot (Robot): The robot to control.
        direction (float): Control direction.
        speed (float): Speed in rad/tick or m/tick.
    """
    if robot.selected.type != Joint.JointType.FIXED:
        robot.selected.theta += direction * speed


def TraversePathPlan(rrt: RRTInfo, target_i: int, speed: float) -> int:
    """Moves the robot along the generated path plan.

    Args:
        rrt (RRTInfo): RRTInfo with path information.
        target_i (int): Index of target node to move towards.
        speed (float): Speed to traverse along the path.

    Returns:
        int: The index of the next target node.
    """
    # must run rrt pathplanning first
    if rrt is None or len(rrt.path) <= 2:
        return 0

    # teleport to start if we reached the goal
    if target_i >= len(rrt.path):
        rrt.path[0].configuration.useConfiguration(rrt.robot)
        return 1

    # move towards target
    qcurrent_vec = RobotConfiguration(rrt.robot).asVec()
    qtarget = rrt.path[target_i].configuration
    qtarget_vec = qtarget.asVec()
    dist = np.linalg.norm(qcurrent_vec - qtarget_vec)
    if dist > speed:
        RobotConfiguration(rrt.robot).fromVec(
            qcurrent_vec + (qtarget_vec - qcurrent_vec) * speed / dist
        ).useConfiguration(rrt.robot)
        return target_i
    else:
        qtarget.useConfiguration(rrt.robot)
        return target_i + 1
