from kineval import Robot, World, Vec3
from robots import Cylinder
from pyvistaqt import BackgroundPlotter
import numpy as np

# student implementations
from kineval.init_robot import init_robot
from kineval.forward_kinematics import traverse_robot_FK


class Kineval:
    """A manager class for handling rendering and updates."""

    def __init__(self, robot: Robot, world: World) -> None:
        # scene objects
        self.robot: Robot = robot  # robot
        self.world: World = world  # world container
        # internal managers
        self._window: BackgroundPlotter = None  # window manager
        # visual options
        self.robot_color: Vec3 = np.array([0.0, 0.14, 0.3], float)  # color of robot
        self.joint_color: Vec3 = np.array([1.0, 0.79, 0.0], float)  # color of joints
        self.robot_opacity: float = 0.6  # opacity of robot
        self.joint_opacity: float = 1.0  # opacity of joints
        self.joint_size: float = 0.15  # radius of joint
        # physics options
        self.tick_rate: float = 24  # target no. of updates per second

        # run initializations
        self.initialize()

    def initialize(self) -> None:
        """Runs all the student initialization functions."""
        init_robot(self.robot)

    def run(self) -> None:
        """Runs the full cycle of the program."""
        # create window
        self._window = BackgroundPlotter(show=True, title="Kineval")
        self._window.set_background("white")
        self._window.add_axes()

        # add robot link geoms to window
        for link in self.robot.links:
            geom = link.geom
            geom.prop.SetColor(*self.robot_color)
            geom.prop.SetOpacity(self.robot_opacity)
            self._window.add_actor(geom)

        # create robot joint geoms and add them to window
        for joint in self.robot.joints:
            geom = Cylinder(joint.axis, self.joint_size, 0.5 * self.joint_size)
            geom.prop.SetColor(*self.joint_color)
            geom.prop.SetOpacity(self.joint_opacity)
            self._window.add_actor(geom)
            joint.geom = geom  # add geom to joint to reference in the future

        # add update to main loop
        tick_millis = 1000 // self.tick_rate  # ms between ticks
        self._window.add_callback(self.update, interval=tick_millis)

        # open window
        self._window.app.exec_()

    def update(self) -> None:
        """Runs all the student functions and visual updates."""
        # run student functions
        traverse_robot_FK(self.robot)

        # update visuals
        self.update_robot_render()
        self._window.update()

    def update_robot_render(self) -> None:
        """Updates the robot on the window."""
        # set transform of link geoms
        for link in self.robot.links:
            geom = link.geom
            geom.user_matrix = (
                self.robot.transform
                if link == self.robot.base
                else link.parent.transform
            )

        # set transform of joint geoms
        for joint in self.robot.joints:
            geom = joint.geom
            geom.user_matrix = joint.transform
