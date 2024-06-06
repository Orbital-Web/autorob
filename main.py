from kineval import Kineval, Robot, World
import importlib
import argparse


def load_robot(robot_name: str) -> Robot:
    """Loads a robot based on the provided robot_name.

    Args:
        robot_name (str): name of py file with robot to load.

    Returns:
        Robot: the loaded robot object.
    """
    return importlib.import_module(f"robots.{robot_name}").robot


if __name__ == "__main__":
    # parse cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robot",
        type=str,
        default="robot_mr2",
        help="Name of the py file with the robot you want to load",
    )
    args = parser.parse_args()

    # initialize kineval
    robot = load_robot(args.robot)
    world = World()  # TODO: replace with load_world function in the future
    kineval = Kineval(robot, world)

    # run kineval
    kineval.run()
