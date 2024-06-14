from kineval import (
    Robot,
    World,
    move_robot,
    turn_robot,
    apply_control,
    KinevalWindow,
    KinevalWindowSettings,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication

# student functions
from kineval.init_robot import init_robot
from kineval.forward_kinematics import traverse_robot_FK


class KinevalSettings:
    """Struct for storing full settings for kineval."""

    def __init__(
        self,
        window_settings: KinevalWindowSettings = None,
        tick_rate: float = 60,
        movement_speed: float = 5,
        turn_speed: float = 3,
        control_speed: float = 1,
    ) -> None:
        self.window_settings: KinevalWindowSettings = (
            KinevalWindowSettings() if window_settings is None else window_settings
        )  # # window settings
        self.tick_rate: float = tick_rate  # target updates per second
        self.movement_speed: float = movement_speed  # robot movement speed in m/s
        self.turn_speed: float = turn_speed  # robot turn speed in rad/s
        self.control_speed: float = control_speed  # robot control speed in rad or m/s


class Kineval:
    """A class for managing the entirety of the program."""

    def __init__(
        self,
        robot: Robot,
        world: World,
        settings: KinevalSettings,
    ):
        """Initializes the robot, world, window, and runs any other
        necessary functions.

        Args:
            robot (Robot): The main robot.
            world (World): The world description for the robot.
            settings (KinevalSettings): All settings for the program.
        """
        # class attributes
        self.robot: Robot = robot  # robot
        self.world: World = world  # world container
        self.settings: KinevalSettings = settings  # settings
        self.app = QApplication([])  # QT application to tie everything together.
        self.window: KinevalWindow = KinevalWindow(
            self.robot,
            self.world,
            self.settings.window_settings,
        )  # render window manager

        # add update callback
        tick_millis = 1000 // self.settings.tick_rate  # ms between each tick
        timer = QTimer(self.window)
        timer.timeout.connect(self.update)
        timer.start(tick_millis)

        # TODO:  run student initialization functions
        init_robot(self.robot)

    def run(self):
        """Runs the entire program."""
        self.window.showMaximized()
        self.app.exec_()

    def update(self):
        """Runs all the update functions and handles continuous key
        presses."""
        # control robot with WSAD
        movement_rate = self.settings.movement_speed / self.settings.tick_rate
        if Qt.Key_W in self.window.pressed_keys:
            move_robot(self.robot, [0, 1], movement_rate)
        elif Qt.Key_S in self.window.pressed_keys:
            move_robot(self.robot, [0, -1], movement_rate)
        if Qt.Key_D in self.window.pressed_keys:
            move_robot(self.robot, [1, 0], movement_rate)
        elif Qt.Key_A in self.window.pressed_keys:
            move_robot(self.robot, [-1, 0], movement_rate)

        # turn robot with QE
        turn_rate = self.settings.turn_speed / self.settings.tick_rate
        if Qt.Key_Q in self.window.pressed_keys:
            turn_robot(self.robot, -1, turn_rate)
        elif Qt.Key_E in self.window.pressed_keys:
            turn_robot(self.robot, 1, turn_rate)

        # apply control to joint with UI
        control_rate = self.settings.control_speed / self.settings.tick_rate
        if Qt.Key_U in self.window.pressed_keys:
            apply_control(self.robot, -1, control_rate)
        elif Qt.Key_I in self.window.pressed_keys:
            apply_control(self.robot, 1, control_rate)

        # TODO: run student functions
        traverse_robot_FK(self.robot)

        # update window
        self.window.update()
