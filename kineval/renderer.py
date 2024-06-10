from kineval import (
    Robot,
    World,
    traverse_up_joint,
    traverse_down_joint,
    traverse_adjacent_joint,
    CollapsibleWidget,
    SliderWidget,
    Vec3,
)
from robots import Cylinder, Line
from pyvistaqt import QtInteractor
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QFormLayout,
    QWidget,
    QDockWidget,
    QLabel,
    QCheckBox,
    QLineEdit,
)
import numpy as np


class KinevalWindowSettings:
    """Struct for storing window settings."""

    def __init__(
        self,
        bg_color: Vec3 = None,
        robot_color: Vec3 = None,
        joint_color: Vec3 = None,
        selection_color: Vec3 = None,
        robot_opacity: float = 0.6,
        joint_opacity: float = 1.0,
        joint_size: float = 0.2,
    ) -> None:
        self.bg_color: Vec3 = (
            np.array([0.533, 0.533, 0.533], float) if bg_color is None else bg_color
        )  # color of background (default gray)
        self.robot_color: Vec3 = (
            np.array([0.0, 0.14, 0.3], float) if robot_color is None else robot_color
        )  # color of links (default dark blue)
        self.joint_color: Vec3 = (
            np.array([1.0, 0.8, 0.0], float) if joint_color is None else joint_color
        )  # color of joints (default yellow)
        self.selection_color: Vec3 = (
            np.array([1.0, 0.0, 0.0], float)
            if selection_color is None
            else selection_color
        )  # color of selected joints (default red)
        self.robot_opacity: float = robot_opacity  # opacity of links
        self.joint_opacity: float = joint_opacity  # opacity of joints
        self.joint_size: float = joint_size  # radius of joint


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
        self.gui: QDockWidget = None  # widget for displaying gui control panel

        # initialize window
        super().__init__(parent=None)
        self.setWindowTitle("Kineval")
        self.resize(960, 540)

        # initialize widgets
        self.__create_plotter_widget()
        self.__add_robot_to_plotter()
        self.__add_world_to_plotter()
        self.__create_gui_widget()

    def __create_plotter_widget(self) -> None:
        """Initializes the main plotter widget for displaying the
        world and the robot."""
        # create central widget to show plotter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # specify layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # attach pyvista qt plotter
        self.plotter = QtInteractor(central_widget)
        layout.addWidget(self.plotter)

        # specify plotter settings
        self.plotter.set_background(self.settings.bg_color)
        self.plotter.add_axes()

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

    def __create_gui_widget(self) -> None:
        """Initializes a dock widget for displaying an
        interactive GUI for controlling the program.
        """
        # create dock widget to show gui
        self.gui = QDockWidget("Control Panel", self)
        self.gui.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.gui.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self.gui)

        # create top level group for all settings
        control_panel = CollapsibleWidget("Kineval", QVBoxLayout)
        self.gui.setWidget(control_panel)

        # example below for sub-groups
        g1 = control_panel.add_group("Test", QVBoxLayout)
        g1.content.addWidget(QCheckBox("just_starting"))

        g2 = control_panel.add_group("User Parameters", QFormLayout)
        g2.content.addRow("robot", QLineEdit())
        g2.content.addRow("world", QLineEdit())

        g3 = control_panel.add_group("Display", QVBoxLayout)
        g3content = g3.add_group("Geometries and Axes", QVBoxLayout)
        g3content.content.addWidget(QCheckBox("display_links"))
        g3content.content.addWidget(QCheckBox("display_links_axes"))
        g3content.content.addWidget(QCheckBox("display_base_axes"))
        g3content.content.addWidget(QCheckBox("display_joints"))
        g3content.content.addWidget(QCheckBox("display_joints_axes"))
        g3content.content.addWidget(QCheckBox("display_joints_angles"))
        g3content.content.addWidget(QCheckBox("display_wireframe"))
        g3content.content.addWidget(QCheckBox("display_collision"))

        # display
        display_settings = control_panel.add_group("Display Settings", QVBoxLayout)
        colors_settings = display_settings.add_group("Colors", QVBoxLayout)
        link_colors_settings = colors_settings.add_group("Links", QVBoxLayout)
        joint_colors_settings = colors_settings.add_group("Joints", QVBoxLayout)

        # add slider for link and joint rgbs
        for i, color in enumerate(("r", "g", "b")):

            def set_link_color(val, i=i):
                self.settings.robot_color[i] = val

            link_slider = SliderWidget(
                color, set_link_color, self.settings.robot_color[i]
            )
            link_colors_settings.content.addWidget(link_slider)

            def set_joint_color(val, i=i):
                self.settings.joint_color[i] = val

            joint_slider = SliderWidget(
                color, set_joint_color, self.settings.joint_color[i]
            )
            joint_colors_settings.content.addWidget(joint_slider)

    def update(self) -> None:
        """Does all the visual updates of the window."""
        # update link visuals
        for link in self.robot.links:
            # update link transformation
            link.geom.user_matrix = (
                self.robot.transform
                if link == self.robot.base
                else link.parent.transform
            )
            # update link color
            link.geom.prop.SetColor(*self.settings.robot_color)

        # update joint visuals
        for joint in self.robot.joints:
            # update joint and axis transformation
            joint.geom.user_matrix = joint.transform
            joint.axis_geom.user_matrix = joint.transform
            # update joint color
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

        # detect single key presses
        elif key == Qt.Key_H:  # toggle menu
            self.gui.toggleViewAction().trigger()

        # joint traversal
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
