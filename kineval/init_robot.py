from kineval import Robot


def init_robot(robot: Robot) -> None:
    """Initializes the parent and children structures
    for each joint in the robot.

    Args:
        robot (Robot): The robot the initialize.
    """
    # TODO: YOUR CODE HERE

    # FIXME: remove instructor solution below
    for joint in robot.joints:
        parent = joint.parent
        parent.children.append(joint)

        child = joint.child
        child.parent = joint
