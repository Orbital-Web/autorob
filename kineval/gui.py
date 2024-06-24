from PyQt5.QtWidgets import (
    QLayout,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame,
    QGroupBox,
    QToolButton,
    QSlider,
    QLineEdit,
    QLabel,
)
from PyQt5.QtCore import Qt
from typing import Callable


class VariableDisplayWidget(QWidget):
    """A widget with a label and a variable display."""

    def __init__(self, label: str, default: str) -> None:
        # class attributes
        self.label: QLabel = None  # label widget
        self.display: QLineEdit = None  # display widget
        self.val: str = default  # value of display varaible

        # initialize the widget
        super().__init__()

        # create the label
        self.label = QLabel(label)

        # create the display
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setFixedWidth(125)
        self.display.setText(self.val)

        # create the layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.display)
        self.setLayout(layout)

    def setValue(self, value: str):
        """Sets the value of the widget variable.

        Args:
            value (str): New value to set to.
        """
        self.val = value
        self.display.setText(self.val)


class SliderWidget(QWidget):
    """A widget with a label, slider, and value."""

    def __init__(
        self,
        label: str,
        default: float = 0,
        min_val: float = 0,
        max_val: float = 1,
        update_callback: Callable = None,
    ):
        """If `update_callback` is specified, it will be called along with
        `self.val` as the argument whenever the slider variable is updated.

        Args:
            label (str): The label for the slider.
            update_callback (Callable): Function to call on slider variable update. Defaults to None.
            default (float, optional): Default value of slider variable. Defaults to 0.
            min_val (float, optional): Minimum value of slider variable. Defaults to 0.
            max_val (float, optional): Maximum value of slider variable. Defaults to 1.
        """
        # class attributes
        self.label: QLabel = None  # label widget
        self.slider: QSlider = None  # slider widget
        self.value_display: QLineEdit = None  # value display widget
        self.min_val: float = min_val  # minimum value the slider goes to
        self.val_range: float = max_val - min_val  # range of value for the slider
        self.val: float = min(
            max(default, min_val), max_val
        )  # value of slider variable
        self.update_callback: Callable = update_callback  # function to call on update

        # initialize the widget
        super().__init__()

        # create the label
        self.label = QLabel(label)

        # create the slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        slider_val = int(100 * (default - min_val) / self.val_range)
        self.slider.setValue(slider_val)

        # create the number display
        self.value_display = QLineEdit()
        self.value_display.setReadOnly(False)
        self.value_display.setFixedWidth(50)
        self.onUpdateValue(slider_val)

        # attach callback for when slider and value is edited
        self.slider.valueChanged.connect(self.onUpdateValue)
        self.value_display.returnPressed.connect(self.onUpdateSlider)

        # create the layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_display)
        self.setLayout(layout)

    def setCallback(self, update_callback: Callable):
        """Sets the update callback function.

        Args:
            update_callback (Callable): Function to call on slider variable update.
        """
        self.update_callback = update_callback

    def onUpdateValue(self, slider_val: float):
        """Updates the value display if the slider is dragged.

        Args:
            slider_val (float): value of slider between 0 and 100.
        """
        self.val = self.val_range * (slider_val / 100) + self.min_val
        self.value_display.setText(f"{self.val:.2f}")
        if self.update_callback:
            self.update_callback(self.val)

    def onUpdateSlider(self):
        """Updates the slider when a value is entered.
        Only updates if the value is a valid number within
        the range specified during construction."""
        display_val = self.val_range * (self.slider.value() / 100) + self.min_val
        # set value if it's a valid number
        try:
            value = float(self.value_display.text())
            if self.min_val <= value <= self.min_val + self.val_range:
                slider_val = int(100 * (value - self.min_val) / self.val_range)
                self.slider.setValue(slider_val)
                self.val = value
                if self.update_callback:
                    self.update_callback(self.val)
            # do not set value if it's outside range
            else:
                self.value_display.setText(f"{display_val:.2f}")
        except ValueError:
            self.value_display.setText(f"{display_val:.2f}")


class CollapsibleWidget(QGroupBox):
    """A widget who's content can be collapsed or expanded
    by clicking on the label."""

    def __init__(self, label: str, expanded: bool = False):
        """Initializes the collasible widget.

        Args:
            label (str): The name of the group.
            expanded (bool, optional): Whether the widget starts expanded or not. Defaults to False.
        """
        # class attributes
        self.toggle_button: QToolButton = None  # title of widget (click to toggle)
        self.toggle_frame: QFrame = None  # frame for the content
        self.content: QLayout = QVBoxLayout()  # the layout of the content

        # initialize widget
        super().__init__()
        self.setTitle("")
        self.setFlat(True)

        # create a toggle button
        self.toggle_button = QToolButton(text=label, checkable=True, checked=expanded)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.DownArrow)
        self.toggle_button.clicked.connect(self.onToggle)

        # create a frame to hold the contents
        self.toggle_frame = QFrame()
        self.toggle_frame.setLayout(self.content)

        # create a layout for the collapsible group
        self.toggle_layout = QVBoxLayout()
        self.toggle_layout.addWidget(self.toggle_button)
        self.toggle_layout.addWidget(self.toggle_frame)
        self.toggle_layout.setContentsMargins(0, 0, 0, 0)
        self.toggle_layout.setSpacing(0)
        self.setLayout(self.toggle_layout)

        # set to default state
        self.onToggle(expanded)

    def addWidget(self, widget: QWidget):
        """Adds a widget to the content.

        Args:
            widget (QWidget): Widget to add.
        """
        self.content.addWidget(widget)

    def addGroup(self, label: str, **kwargs) -> "CollapsibleWidget":
        """Creates a new CollapsibleWidget as a child of the
        current widget.

        Args:
            label (str): Group name of child CollapsibleWidget.

        Returns:
            CollapsibleWidget: The child CollapsibleWidget.
        """
        group = CollapsibleWidget(label, **kwargs)
        self.content.addWidget(group)
        return group

    def onToggle(self, checked: bool):
        """Updates the arrow to either facing down or right
        depending on the state of the collapsible widget.

        Args:
            checked (bool): Whether the content is expanded or not.
        """
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.toggle_frame.setVisible(checked)
