from .robot import Robot

# EXAMPLE: from project3 import fk_robot
# from project4 import check_collision


class Kineval:
    """A manager class for handling rendering and updates."""

    def __init__(self) -> None:
        self.robot: Robot = None
        self.obstacles: list = []
        # maybe add settings to controll color of robot & world, etc.

    def update(self) -> None:
        """The main update loop for the world."""
        # EXAMPLE: fk_robot(self.robot)
        # collisions = check_collision(self.robot)
        # call other student implemented functions
        self.render_robot()  # maybe pass in collision to highlight them

    def render_robot(self) -> None:
        """
        Renders each link and joint of `self.robot`.
        Joints are drawn using `transform` and `axis`.
        Links are drawn using `_mesh`, `xyz, `rpy`, and the parent
        joint's `transform`.
        """
        for link in self.robot.links:
            mesh = link._mesh
            xyz = link.xyz
            rpy = link.rpy
            transform = link.parent.transform
            # render link

        for joint in self.robot.joints:
            mesh = None  # create a cyliner mesh
            transform = joint.transform
            # render joint
            axis_mesh = None  # create a line for the axis
            axis = joint.axis
            # render axis
