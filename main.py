from kineval import Kineval, KinevalSettings, Robot, World
import importlib
import argparse


def load_robot(robot_name: str) -> Robot:
    """Loads a robot based on the provided `robot_name`.

    Args:
        robot_name (str): name of py file with robot to load.

    Returns:
        Robot: the loaded robot object.
    """
    return importlib.import_module(f"robots.{robot_name}").robot


def load_world(world_name: str) -> World:
    """Loads a world based on the provided `world_name`.

    Args:
        world_name (str): name of py file with world to load.

    Returns:
        World: the loaded world object.
    """
    return importlib.import_module(f"worlds.{world_name}").world


if __name__ == "__main__":
    # parse cli arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r",
        "--robot",
        type=str,
        default="robot_mr2",
        help="Name of the py file with the robot you want to load",
    )
    parser.add_argument(
        "-w",
        "--world",
        type=str,
        default="world_basic",
        help="Name of the py file with the world you want to load",
    )
    args = parser.parse_args()

    # initialize kineval
    robot = load_robot(args.robot)
    world = load_world(args.world)
    settings = KinevalSettings()  # use default settings
    kineval = Kineval(robot, world, settings)

    # run kineval
    kineval.run()
