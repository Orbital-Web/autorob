from kineval import (
    Robot,
    World,
    traverse_up_joint,
    traverse_down_joint,
    traverse_adjacent_joint,
    Vec3,
)
from robots import Cylinder, Line
from pyvistaqt import QtInteractor
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from dataclasses import dataclass, field
import numpy as np


@dataclass
class KinevalWindowSettings:
    """Struct for storing window settings."""

    bg_color: Vec3 = field(
        default_factory=lambda: np.array([0.533, 0.533, 0.533], float)
    )  # color of background (default gray)
    robot_color: Vec3 = field(
        default_factory=lambda: np.array([0.0, 0.14, 0.3], float)
    )  # color of robot (default dark blue)
    joint_color: Vec3 = field(
        default_factory=lambda: np.array([1.0, 0.79, 0.0], float)
    )  # color of joints (default yellow)
    selection_color: Vec3 = field(
        default_factory=lambda: np.array([1.0, 0.0, 0.0], float)
    )  # color of selected joints (default red)
    robot_opacity: float = 0.6  # opacity of robot
    joint_opacity: float = 1.0  # opacity of joints
    joint_size: float = 0.2  # radius of joint


class KinevalWindow(QMainWindow):
    """Class for handling the window and rendering."""

    def __init__(
        self,
        robot: Robot,
        world: World,
        settings: KinevalWindowSettings,
    ) -> None:
        # class attributes
        self.robot: Robot = robot  # robot
        self.world: World = world  # world container
        self.settings: KinevalWindowSettings = settings  # settings
        self.detect_keys = {  # set of keys to detect
            Qt.Key_W,  # front
            Qt.Key_S,  # back
            Qt.Key_A,  # left
            Qt.Key_D,  # right
            Qt.Key_Q,  # turn left
            Qt.Key_E,  # turn right
            Qt.Key_U,  # apply positive control
            Qt.Key_I,  # apply negative control
        }
        self.pressed_keys = set()  # currently pressed keys
        self.previous_camera_pos: Vec3 = [0, 0, 0]  # last valid camera position
        self.plotter: QtInteractor = None  # main widget for drawing robots & world

        # initialize window
        super().__init__(parent=None)
        self.setWindowTitle("Kineval")

        # initialize widgets
        self.__create_plotter_widget()
        self.__add_robot_to_plotter()
        self.__add_world_to_plotter()

    def __create_plotter_widget(self) -> None:
        """Initializes the main plotter widget for displaying the
        world and the robot."""
        # create central widget to show plotter
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # specify layout
        layout = QVBoxLayout(central_widget)

        # attach pyvista qt plotter
        self.plotter = QtInteractor(central_widget)
        layout.addWidget(self.plotter)

        # specify plotter settings
        self.plotter.set_background(self.settings.bg_color)

        # attach different callbacks
        self.plotter.keyPressEvent = self.on_key_press
        self.plotter.keyReleaseEvent = self.on_key_release
        self.plotter.iren.add_observer("InteractionEvent", self.on_camera_move)

    def __add_robot_to_plotter(self) -> None:
        """Creates and adds the robot link and joint geometries
        to the plotter widget."""
        # add robot link geoms to window
        for link in self.robot.links:
            link.geom.prop.SetColor(*self.settings.robot_color)
            link.geom.prop.SetOpacity(self.settings.robot_opacity)
            self.plotter.add_actor(link.geom)

        # create robot joint geoms and add them to window
        for joint in self.robot.joints:
            # joint geom
            joint.geom = Cylinder(
                joint.axis, self.settings.joint_size, 0.5 * self.settings.joint_size
            )
            joint.geom.prop.SetColor(*self.settings.joint_color)
            joint.geom.prop.SetOpacity(self.settings.joint_opacity)
            self.plotter.add_actor(joint.geom)

            # joint axis geom
            joint.axis_geom = Line(
                np.zeros((3), float), joint.axis, 2 * self.settings.joint_size, 2
            )
            self.plotter.add_actor(joint.axis_geom)

    def __add_world_to_plotter(self) -> None:
        """Creates and adds the terrain and obstacle geometries
        to the plotter widget."""
        pass

    def update(self):
        """Does all the visual updates of the window."""
        # update link visuals
        for link in self.robot.links:
            # update link transformation
            link.geom.user_matrix = (
                self.robot.transform
                if link == self.robot.base
                else link.parent.transform
            )

        # update joint visuals
        for joint in self.robot.joints:
            # update joint and axis transformation
            joint.geom.user_matrix = joint.transform
            joint.axis_geom.user_matrix = joint.transform
            # reset color
            joint.geom.prop.SetColor(*self.settings.joint_color)

        # update color of selected joint
        self.robot.selected.geom.prop.SetColor(*self.settings.selection_color)

        # update plotter widget
        self.plotter.update()

    def on_key_press(self, event: QKeyEvent) -> None:
        """Adds key to `pressed_key` if it has been pressed and is
        in `detect_keys`. Additionally runs commands that should
        only run once after a key press rather than while the key
        is presssed.

        Args:
            event (QKeyEvent): The key pressed event object.
        """
        key = event.key()  # pressed key
        if key in self.detect_keys and key not in self.pressed_keys:
            self.pressed_keys.add(key)

        # detect only first key down
        elif key == Qt.Key_J:  # traverse up joint
            traverse_up_joint(self.robot)
        elif key == Qt.Key_K:  # traverse down joint
            traverse_down_joint(self.robot)
        elif key == Qt.Key_L:  # traverse adjacent joint
            traverse_adjacent_joint(self.robot)

    def on_key_release(self, event: QKeyEvent) -> None:
        """Removes key from `pressed_key` if it has been released.

        Args:
            event (QKeyEvent): The key released event object.
        """
        key = event.key()  # released key
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def on_camera_move(self, caller, event) -> None:
        """Ensures the camera pivots around the robot base."""
        # update camera to pivot base
        center = self.robot.base.geom.GetCenter()
        self.plotter.camera.SetFocalPoint(center)

        # Prevent camera from rolling
        self.plotter.camera.SetViewUp([0, 0, 1])

        # Ensure camera does not orbit past the center
        view_vec = np.array(self.plotter.camera.position) - center
        view_vec /= np.linalg.norm(view_vec)
        if abs(view_vec[2]) > 0.995:
            self.plotter.camera.SetPosition(self.previous_camera_pos)
        else:
            self.previous_camera_pos = self.plotter.camera.position