from .robot import Robot
from robots.helpers import Cylinder
import pyvista as pv
import numpy as np

from .types import Vec3

# EXAMPLE: from project3 import fk_robot
# from project4 import check_collision


class Kineval:
    """A manager class for handling rendering and updates."""

    def __init__(self, robot: Robot) -> None:
        self.robot: Robot = robot
        self.obstacles: list = []
        self._plotter: pv.Plotter = None
        # visual options
        self.robot_color: Vec3 = np.array([0.0, 0.14, 0.3], float)
        self.joint_color: Vec3 = np.array([1.0, 0.79, 0.0], float)
        self.robot_opacity: float = 0.8
        self.joint_opacity: float = 1.0
        self.joint_size: float = 0.15

    def open_window(self):
        """Run once to open a window showing the scene"""
        if self._plotter is None or self._plotter._closed:
            # create window
            self._plotter = pv.Plotter()
            self._plotter.set_background("white")
            self._plotter.add_axes()

            # add robot geom to plotter
            if self.robot:
                for link in self.robot.links:
                    geom = link.geom
                    geom.prop.SetColor(*self.robot_color)
                    geom.prop.SetOpacity(self.robot_opacity)
                    self._plotter.add_actor(geom)

                for joint in self.robot.joints:
                    geom = Cylinder(joint.axis, self.joint_size, 0.5 * self.joint_size)
                    geom.prop.SetColor(*self.joint_color)
                    geom.prop.SetOpacity(self.joint_opacity)
                    self._plotter.add_actor(geom)
                    joint.geom = geom  # add to joint to reference in the future

            self._plotter.show(interactive_update=True)  # interactive_update=True

    def wait_until_window_closed(self):
        """Prevents the window from automatically closing."""
        self._plotter.show()

    def update(self) -> None:
        """The main update loop for the world."""
        # EXAMPLE: fk_robot(self.robot)
        # collisions = check_collision(self.robot)
        # call other student implemented functions
        if self._plotter:
            self.update_robot_render()
            self._plotter.update()

    def update_robot_render(self) -> None:
        """Updates the robot on the window."""
        for link in self.robot.links:
            geom = link.geom
            geom.user_matrix = (
                self.robot.transform
                if link == self.robot.base
                else link.parent.transform
            )

        for joint in self.robot.joints:
            geom = joint.geom
            geom.user_matrix = joint.transform
