from kineval import (
    Robot,
    World,
    Cylinder,
    Line,
    traverse_up_joint,
    traverse_down_joint,
    traverse_adjacent_joint,
    CollapsibleWidget,
    SliderWidget,
    VariableDisplayWidget,
    Vec3,
)
from pyvistaqt import QtInteractor
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QDockWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
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
        terrain_color: Vec3 = None,
        robot_opacity: float = 0.8,
        joint_opacity: float = 1.0,
        joint_size: float = 0.2,
        terrain_opacity: float = 0.8,
    ) -> None:
        self.bg_color: Vec3 = (
            np.array([0.533, 0.533, 0.533], float)
            if bg_color is None
            else np.array(bg_color, float)
        )  # color of background (default gray)
        self.robot_color: Vec3 = (
            np.array([0.0, 0.14, 0.3], float)
            if robot_color is None
            else np.array(robot_color, float)
        )  # color of links (default dark blue)
        self.joint_color: Vec3 = (
            np.array([1.0, 0.8, 0.0], float)
            if joint_color is None
            else np.array(joint_color, float)
        )  # color of joints (default yellow)
        self.selection_color: Vec3 = (
            np.array([1.0, 0.0, 0.0], float)
            if selection_color is None
            else np.array(selection_color, float)
        )  # color of selected joints (default red)
        self.terrain_color: Vec3 = (
            np.array([0.4, 0.73, 0.4], float)
            if terrain_color is None
            else np.array(terrain_color, float)
        )  # color of terrain (default light green)
        self.robot_opacity: float = robot_opacity  # opacity of links
        self.joint_opacity: float = joint_opacity  # opacity of joints
        self.joint_size: float = joint_size  # radius of joint
        self.terrain_opacity: float = terrain_opacity  # opacity of terrain


class KinevalWindow(QMainWindow):
    """Class for handling the window and rendering."""

    def __init__(
        self,
        robot: Robot,
        world: World,
        settings: KinevalWindowSettings,
    ) -> None:
        """Initializes the plotter and gui for the window.

        Args:
            robot (Robot): Kineval robot.
            world (World): Kineval world.
            settings (KinevalWindowSettings): Settings for the window and visuals.
        """
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

    def __create_plotter_widget(self):
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

    def __add_robot_to_plotter(self):
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
                [0.0, 0.0, 0.0],
                joint.axis,
                self.settings.joint_size,
                0.5 * self.settings.joint_size,
            )
            joint.geom.prop.SetColor(*self.settings.joint_color)
            joint.geom.prop.SetOpacity(self.settings.joint_opacity)
            self.plotter.add_actor(joint.geom)

            # joint axis geom
            joint.axis_geom = Line(
                [0.0, 0.0, 0.0], joint.axis, 2 * self.settings.joint_size, 2
            )
            self.plotter.add_actor(joint.axis_geom)

        # highlight selected joint
        self.robot.selected.geom.prop.SetColor(*self.settings.selection_color)

        # set up camera
        center = self.robot.base.geom.GetCenter()
        self.plotter.camera.SetFocalPoint(center)

    def __add_world_to_plotter(self):
        """Creates and adds the terrain and obstacle geometries
        to the plotter widget."""
        self.plotter.add_actor(self.world.terrain)
        self.world.terrain.prop.SetColor(*self.settings.terrain_color)
        self.world.terrain.prop.SetOpacity(self.settings.terrain_opacity)

    def __create_gui_widget(self):
        """Initializes a dock widget for displaying an
        interactive GUI for controlling the program."""
        # create dock widget to show gui
        self.gui = QDockWidget("Control Panel")
        self.gui.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.gui.setFeatures(
            QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable
        )
        self.addDockWidget(Qt.RightDockWidgetArea, self.gui)

        # create scroll area and gui layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumWidth(288)
        self.gui.setWidget(scroll)
        gui_layout = QVBoxLayout()
        scroll.setLayout(gui_layout)

        # show information (robot and world)
        info_display = CollapsibleWidget("Info", expanded=True)
        gui_layout.addWidget(info_display)
        robot_info = info_display.add_group("Robot", expanded=True)
        robot_info.addWidget(VariableDisplayWidget("Robot", self.robot.name))
        robot_info.addWidget(VariableDisplayWidget("Base", self.robot.base.name))
        robot_info.addWidget(
            VariableDisplayWidget("Selection", self.robot.selected.name)
        )
        world_info = info_display.add_group("World", expanded=True)
        world_info.addWidget(VariableDisplayWidget("World", self.world.name))

        # display settings (link, joints, world)
        display_settings = CollapsibleWidget("Display Settings")
        gui_layout.addWidget(display_settings)
        link_settings = display_settings.add_group("Links")
        joint_settings = display_settings.add_group("Joints")
        world_settings = display_settings.add_group("World")

        # add toggle for link, joint, and terrain display
        link_toggle = QCheckBox("Show Links", checked=True)
        link_toggle.toggled.connect(lambda: self.update_link_visibility(link_toggle))
        link_settings.addWidget(link_toggle)
        joint_toggle = QCheckBox("Show Joints", checked=True)
        joint_toggle.toggled.connect(lambda: self.update_joint_visibility(joint_toggle))
        joint_settings.addWidget(joint_toggle)
        axis_toggle = QCheckBox("Show Joint Axes", checked=False)
        self.update_axis_visibility(axis_toggle)
        axis_toggle.toggled.connect(lambda: self.update_axis_visibility(axis_toggle))
        joint_settings.addWidget(axis_toggle)
        terrain_toggle = QCheckBox("Show Terrain", checked=True)
        terrain_toggle.toggled.connect(
            lambda: self.update_terrain_visibility(terrain_toggle)
        )
        world_settings.addWidget(terrain_toggle)

        # add slider for link, joint, and terrain rgbs
        joint_settings.addWidget(QLabel("Joint"))
        for i, color in enumerate(("r", "g", "b")):
            # link color
            link_color_slider = SliderWidget(color, self.settings.robot_color[i])
            link_color_slider.set_callback(
                lambda val, i=i: self.update_link_color(val, i),
            )
            link_settings.addWidget(link_color_slider)
            # joint color
            joint_color_slider = SliderWidget(color, self.settings.joint_color[i])
            joint_color_slider.set_callback(
                lambda val, i=i: self.update_joint_color(val, i)
            )
            joint_settings.addWidget(joint_color_slider)
            # terrain color
            terrain_color_slider = SliderWidget(color, self.settings.terrain_color[i])
            terrain_color_slider.set_callback(
                lambda val, i=i: self.update_terrain_color(val, i)
            )
            world_settings.addWidget(terrain_color_slider)

        # add slider for selected joint rgbs
        joint_settings.addWidget(QLabel("Selected Joint"))
        for i, color in enumerate(("r", "g", "b")):
            select_color_slider = SliderWidget(color, self.settings.selection_color[i])
            select_color_slider.set_callback(
                lambda val, i=i: self.update_selection_color(val, i)
            )
            joint_settings.addWidget(select_color_slider)

        # add spacing to push collapsed content to the top
        gui_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

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
            # update link color
            link.geom.prop.SetColor(*self.settings.robot_color)

        # update joint visuals
        for joint in self.robot.joints:
            # update joint and axis transformation
            joint.geom.user_matrix = joint.transform
            joint.axis_geom.user_matrix = joint.transform

        # update plotter widget
        self.plotter.update()

    def on_key_press(self, event: QKeyEvent):
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
            traverse_up_joint(
                self.robot, self.settings.joint_color, self.settings.selection_color
            )
        elif key == Qt.Key_K:  # traverse down joint
            traverse_down_joint(
                self.robot, self.settings.joint_color, self.settings.selection_color
            )
        elif key == Qt.Key_L:  # traverse adjacent joint
            traverse_adjacent_joint(
                self.robot, self.settings.joint_color, self.settings.selection_color
            )

    def on_key_release(self, event: QKeyEvent):
        """Removes key from `pressed_key` if it has been released.

        Args:
            event (QKeyEvent): The key released event object.
        """
        key = event.key()  # released key
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def on_camera_move(self, caller, event):
        """Ensures the camera pivots around the robot base."""
        # update camera to pivot base
        center = self.robot.base.geom.GetCenter()
        self.plotter.camera.SetFocalPoint(center)

        # calculate camera components
        view_dir = self.plotter.camera.GetDirectionOfProjection()
        up_dir = self.plotter.camera.GetViewUp()
        right_dir = np.cross(view_dir, up_dir)

        # disable camera roll
        right_dir[2] = 0
        right_dir /= np.linalg.norm(right_dir)
        self.plotter.camera.SetViewUp(np.cross(right_dir, view_dir).tolist())

    def update_link_color(self, value: float, index: int):
        """Updates `self.settings.robot_color` at index `index`,
        and the updates the link geometry colors.

        Args:
            value (float): Value of slider to set to.
            index (int): Color index to modify. 0=r, 1=g, 2=b.
        """
        self.settings.robot_color[index] = value

        # add update robot link geom colors
        for link in self.robot.links:
            link.geom.prop.SetColor(*self.settings.robot_color)

    def update_joint_color(self, value: float, index: int):
        """Updates `self.settings.joint_color` at index `index`,
        and the updates the joint geometry colors.

        Args:
            value (float): Value of slider to set to.
            index (int): Color index to modify. 0=r, 1=g, 2=b.
        """
        self.settings.joint_color[index] = value

        # add update robot joint geom colors
        for joint in self.robot.joints:
            joint.geom.prop.SetColor(*self.settings.joint_color)

        # highlight selected joint
        self.robot.selected.geom.prop.SetColor(*self.settings.selection_color)

    def update_selection_color(self, value: float, index: int):
        """Updates `self.settings.selection_color` at index `index`,
        and the updates the selected joint's geometry color.

        Args:
            value (float): Value of slider to set to.
            index (int): Color index to modify. 0=r, 1=g, 2=b.
        """
        self.settings.selection_color[index] = value
        self.robot.selected.geom.prop.SetColor(*self.settings.selection_color)

    def update_terrain_color(self, value: float, index: int):
        """Updates `self.settings.terrain_color` at index `index`,
        and the updates the terrain geometry color.

        Args:
            value (float): Value of slider to set to.
            index (int): Color index to modify. 0=r, 1=g, 2=b.
        """
        self.settings.terrain_color[index] = value
        self.world.terrain.prop.SetColor(*self.settings.terrain_color)

    def update_link_visibility(self, button: QCheckBox):
        """Sets link visibility.

        Args:
            button (QCheckButton): Button used for toggle.
        """
        for link in self.robot.links:
            link.geom.SetVisibility(button.isChecked())

    def update_joint_visibility(self, button: QCheckBox):
        """Sets joint visibility.

        Args:
            button (QCheckButton): Button used for toggle.
        """
        for joint in self.robot.joints:
            joint.geom.SetVisibility(button.isChecked())

    def update_axis_visibility(self, button: QCheckBox):
        """Sets joint axis visibility.

        Args:
            button (QCheckButton): Button used for toggle.
        """
        for joint in self.robot.joints:
            joint.axis_geom.SetVisibility(button.isChecked())

    def update_terrain_visibility(self, button: QCheckBox):
        """Sets world terrain visibility.

        Args:
            button (QCheckBox): Button used for toggle.
        """
        self.world.terrain.SetVisibility(button.isChecked())
