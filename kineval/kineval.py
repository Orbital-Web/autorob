from kineval import (
    Robot,
    World,
    move_robot,
    turn_robot,
    traverse_up_joint,
    traverse_down_joint,
    traverse_adjacent_joint,
    apply_control,
    Vec3,
)
from robots import Cylinder, Line
from pyvistaqt import BackgroundPlotter
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from dataclasses import dataclass, field
import numpy as np

# student implementations
from kineval.init_robot import init_robot
from kineval.forward_kinematics import traverse_robot_FK


@dataclass
class KinevalVisualSettings:
    """Struct for storing visual settings."""

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


class KinevalRenderer(BackgroundPlotter):
    """A class for handling rendering and keybinds."""

    def __init__(
        self,
        robot: Robot,
        world: World,
        visual_settings: KinevalVisualSettings,
        *args,
        **kwargs,
    ) -> None:
        self.robot: Robot = robot  # robot
        self.world: World = world  # world container
        self.settings: KinevalVisualSettings = visual_settings  # settings
        self.detect_keys = {
            Qt.Key_W,  # front
            Qt.Key_S,  # back
            Qt.Key_A,  # left
            Qt.Key_D,  # right
            Qt.Key_Q,  # turn left
            Qt.Key_E,  # turn right
            Qt.Key_U,  # apply positive control
            Qt.Key_I,  # apply negative control
        }  # set of keys to detect (for continuous pressing)
        self.pressed_keys = set()  # currently pressed keys

        # initialize window
        super().__init__(show=True, *args, **kwargs)
        self.set_background(self.settings.bg_color)
        self.add_axes()

        # control camera orbit
        self.iren.add_observer("InteractionEvent", self.on_camera_move)
        self.previous_camera_pos = self.camera.position  # last valid camera position

        # add objects to window
        self.__add_robot()
        self.__add_world()

    def __add_robot(self) -> None:
        """Creates and adds the robot link and joint geometries
        to the window."""
        # add robot link geoms to window
        for link in self.robot.links:
            geom = link.geom
            geom.prop.SetColor(*self.settings.robot_color)
            geom.prop.SetOpacity(self.settings.robot_opacity)
            self.add_actor(geom)

        # create robot joint geoms and add them to window
        for joint in self.robot.joints:
            # joint geom
            geom = Cylinder(
                joint.axis, self.settings.joint_size, 0.5 * self.settings.joint_size
            )
            geom.prop.SetColor(*self.settings.joint_color)
            geom.prop.SetOpacity(self.settings.joint_opacity)
            self.add_actor(geom)
            joint.geom = geom  # add geom to joint to reference later

            # joint axis geom
            axis_geom = Line(
                np.zeros((3), float), joint.axis, 2 * self.settings.joint_size, 2
            )
            self.add_actor(axis_geom)
            joint.axis_geom = axis_geom  # add axis geom to joint to reference later

    def __add_world(self) -> None:
        """Adds terrain and obstacle geometries to the window."""
        pass

    def open_window(self) -> None:
        """Opens the window."""
        self.app.exec_()

    def update_visuals(self) -> None:
        """Updates all the objects on the window."""
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

        # update window
        self.update()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Adds key to `pressed_key` if it has been
        pressed and is in `detect_keys`.

        Args:
            event (QKeyEvent): The key press event object.
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

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """Removes key from `pressed_key` if it has been
        released.

        Args:
            event (QKeyEvent): The key release event object.
        """
        key = event.key()  # released key
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def on_camera_move(self, caller, event) -> None:
        """Ensures the camera pivots around the robot base."""
        # update camera to pivot base
        center = self.robot.base.geom.GetCenter()
        self.camera.SetFocalPoint(center)

        # Prevent camera from rolling
        self.camera.SetViewUp([0, 0, 1])

        # Ensure camera does not orbit past the center
        view_vec = np.array(self.camera.position) - center
        view_vec /= np.linalg.norm(view_vec)
        if abs(view_vec[2]) > 0.995:
            self.camera.SetPosition(self.previous_camera_pos)
        else:
            self.previous_camera_pos = self.camera.position


class Kineval:
    """A class for handling the lifecycle of the program."""

    def __init__(
        self,
        robot: Robot,
        world: World,
        visual_settings: KinevalVisualSettings,
        tick_rate: float = 60,
    ) -> None:
        self.robot: Robot = robot  # robot
        self.world: World = world  # world container
        self.visual_settings: KinevalVisualSettings = visual_settings  # window settings
        self.tick_rate: float = tick_rate  # target no. of updates per second
        self.renderer: KinevalRenderer = None  # render window manager

        # run student initialization functions
        init_robot(self.robot)

        # other initializations
        self.robot.selected = self.robot.joints[0]

    def run(self) -> None:
        """Starts the program."""
        # create renderer
        self.renderer = KinevalRenderer(
            self.robot, self.world, self.visual_settings, title="Kineval"
        )

        # set update to run at tick rate
        tick_millis = 1000 // self.tick_rate  # ms between ticks
        self.renderer.add_callback(self.update, interval=tick_millis)

        # open window
        self.renderer.open_window()

    def update(self) -> None:
        """Runs all the student functions and visual updates."""
        # control robot with WSAD
        if Qt.Key_W in self.renderer.pressed_keys:
            move_robot(self.robot, [0, 1], 5 / self.tick_rate)
        elif Qt.Key_S in self.renderer.pressed_keys:
            move_robot(self.robot, [0, -1], 5 / self.tick_rate)
        if Qt.Key_D in self.renderer.pressed_keys:
            move_robot(self.robot, [1, 0], 5 / self.tick_rate)
        elif Qt.Key_A in self.renderer.pressed_keys:
            move_robot(self.robot, [-1, 0], 5 / self.tick_rate)

        # turn robot with QE
        if Qt.Key_Q in self.renderer.pressed_keys:
            turn_robot(self.robot, -1, 3 / self.tick_rate)
        elif Qt.Key_E in self.renderer.pressed_keys:
            turn_robot(self.robot, 1, 3 / self.tick_rate)

        # apply control to joint with UI
        if Qt.Key_U in self.renderer.pressed_keys:
            apply_control(self.robot, -1, 1 / self.tick_rate)
        elif Qt.Key_I in self.renderer.pressed_keys:
            apply_control(self.robot, 1, 1 / self.tick_rate)

        # run student functions
        traverse_robot_FK(self.robot)

        # update visuals
        self.renderer.update_visuals()
