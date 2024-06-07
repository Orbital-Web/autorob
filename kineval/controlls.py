from kineval import Robot, Vec2, Vec3
import numpy as np


def move_robot(robot: Robot, direction: Vec2, speed: float):
    """Moves the robot in the specified direction.
    Increments `robot.xyz` by some vector v with magnitude
    `speed`, depending on `robot.facing` and `direction`.

    Args:
        robot (Robot): The robot to move.
        direction (Vec2): Direction to move in. One of [1, 0], [-1, 0], [0, 1], or [0, -1].
    """
    up = np.array([0, 0, 1])  # up direction vector
    facing = robot.facing  # vector of forward direction
    lateral = np.cross(up, facing)  # vector of right direction

    if direction[0]:  # forward-backwards
        robot.xyz += direction[0] * speed * facing
    else:  # right-left
        robot.xyz += direction[1] * speed * lateral


def traverse_up_joint(robot: Robot):
    pass


def traverse_down_joint(robot: Robot):
    pass


def traverse_adjacent_joint(robot: Robot):
    pass
