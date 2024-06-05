from kineval import Kineval, Robot

# from robots.robot_mr2 import robot
import importlib
import argparse


def load_robot(robot_name: str) -> Robot:
    """Loads a robot based on the provided robot_name"""
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
    kineval = Kineval(robot)

    kineval.open_window()
    for i in range(100):
        # robot.joints[1].transform[0, 3] += 0.1
        kineval.update()
    kineval.wait_until_window_closed()
