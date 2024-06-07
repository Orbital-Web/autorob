from kineval import Robot, Vec2
from scipy.spatial.transform import Rotation as R
import numpy as np


def move_robot(robot: Robot, direction: Vec2, speed: float):
    """Moves the robot in the specified direction.
    Increments `robot.xyz` by some vector v with magnitude
    `speed`, depending on `robot.facing` and `direction`.

    Args:
        robot (Robot): The robot to move.
        direction (Vec2): Move direction in +x and +y axis.
        speed (float): Speed of movement in m/tick.
    """
    up = np.array([0, 0, 1])  # up direction vector
    facing = robot.facing  # vector of forward direction
    lateral = np.cross(up, facing)  # vector of right direction

    robot.xyz += direction[0] * speed * facing
    robot.xyz += direction[1] * speed * lateral


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
    pass


def traverse_down_joint(robot: Robot):
    pass


def traverse_adjacent_joint(robot: Robot):
    pass
