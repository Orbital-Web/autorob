from kineval import Robot, Vec2
from scipy.spatial.transform import Rotation as R
import numpy as np
from pyvista.plotting.camera import Camera


def move_robot(robot: Robot, direction: Vec2, speed: float):
    """Moves the robot in the specified direction.
    Increments `robot.xyz` by some vector v with magnitude
    `speed`, depending on `robot.facing` and `direction`.
    Also moves the camera.

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

    # update camera position
    # camera_position = camera.position
    # camera.SetPosition(
    #     [
    #         camera_position[0] + dxyz[0],
    #         camera_position[1] + dxyz[1],
    #         camera_position[2] + dxyz[2],
    #     ]
    # )
    # camera.SetFocalPoint(robot.base.geom.GetCenter())


def turn_robot(robot: Robot, direction: float, speed: float):
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


def traverse_up_joint(robot: Robot):
    """Selects the next joint down the kinematic
    hierarchy.

    Args:
        robot (Robot): The robot to traverse.
    """
    # select first child joint of child link
    if robot.selected.child.children:
        robot.selected = robot.selected.child.children[0]


def traverse_down_joint(robot: Robot):
    """Selects the previous joint down the kinematic
    hierarchy.

    Args:
        robot (Robot): The robot to traverse.
    """
    # select parent joint of parent link
    if robot.selected.parent.parent:
        robot.selected = robot.selected.parent.parent


def traverse_adjacent_joint(robot: Robot):
    """Selects the adjacent joint of the same link.

    Args:
        robot (Robot): The robot to traverse.
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
    robot.selected = child_joints[(i + 1) % n_children]


def apply_control(robot: Robot, direction: float, speed: float):
    """Modifies the robot's selected joint's theta in the
    specified direction. Turns the robot's selected joint
    if the joint is continuous or revolute. Extends or
    retracts the joint if the joint is prismatic.

    Args:
        robot (Robot): The robot to control.
        direction (float): Control direction.
        speed (float): Speed in rad/tick or m/tick.
    """
    robot.selected.theta += direction * speed
