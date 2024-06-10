from PyQt5.QtWidgets import (
    QLayout,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFrame,
    QGroupBox,
    QToolButton,
    QSpacerItem,
    QSizePolicy,
    QSlider,
    QLineEdit,
    QLabel,
)
from PyQt5.QtCore import Qt
from typing import Type, Callable


class SliderWidget(QWidget):
    """A widget with a label, slider, and value.
    `val` stores the value of the slider variable, and `update_callback`
    is called with `val` every time the variables updates."""

    def __init__(
        self,
        label: str,
        update_callback: Callable,
        default: float = 0,
        min_val: float = 0,
        max_val: float = 1,
    ):
        # class attributes
        self.label: QLabel = None  # label widget
        self.slider: QSlider = None  # slider widget
        self.value_display: QLineEdit = None  # value display widget
        self.min_val: float = min_val  # minimum value the slider goes to
        self.val_range: float = max_val - min_val  # range of value for the slider
        self.val: float = min(max(default, min_val), max_val)  # value of slider var
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
        self.update_value_display(slider_val)

        # attach callback for when slider and value is edited
        self.slider.valueChanged.connect(self.update_value_display)
        self.value_display.returnPressed.connect(self.update_slider)

        # create the layout
        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_display)
        self.setLayout(layout)

    def update_value_display(self, slider_val: float):
        """Updates the value display if the slider is dragged.

        Args:
            slider_val (float): value of slider between 0 and 100.
        """
        self.val = self.val_range * (slider_val / 100) + self.min_val
        self.value_display.setText(f"{self.val:.2f}")
        self.update_callback(self.val)

    def update_slider(self):
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
                self.update_callback(self.val)
            # do not set value if it's outside range
            else:
                self.value_display.setText(f"{display_val:.2f}")
        except ValueError:
            self.value_display.setText(f"{display_val:.2f}")


class CollapsibleWidget(QGroupBox):
    """A widget who's content can be collapsed or expanded
    by clicking on its title. It's layout can be accessed for
    formatting and adding sub-widgets through the `content`
    attribute."""

    def __init__(self, title: str, layout_class: Type[QLayout]) -> None:
        # class attributes
        self.toggle_button: QToolButton = None  # title of widget (click to toggle)
        self.toggle_frame: QFrame = None  # frame for the content
        self.content: QLayout = layout_class()  # the layout of the content

        # initialize widget
        super().__init__()
        self.setTitle("")
        self.setFlat(True)

        # create a toggle button
        self.toggle_button = QToolButton(text=title, checkable=True)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.DownArrow)
        self.toggle_button.clicked.connect(self.on_toggled)

        # create a frame to hold the contents
        self.toggle_frame = QFrame()
        self.toggle_frame.setLayout(self.content)

        # create a layout for the collapsible group
        self.toggle_layout = QVBoxLayout()
        self.toggle_layout.addWidget(self.toggle_button)
        self.toggle_layout.addWidget(self.toggle_frame)
        self.toggle_layout.setContentsMargins(0, 0, 0, 0)
        self.toggle_layout.setSpacing(0)

        # set the layout for the collapsible group
        self.setLayout(self.toggle_layout)

        # add spacer to push content up when collapsed
        self.toggle_layout.addSpacerItem(
            QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def on_toggled(self, checked: bool):
        """Updates the arrow to either facing down or right
        depending on the state of the collapsible widget.

        Args:
            checked (bool): Whether the content is expanded or not.
        """
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.toggle_frame.setVisible(checked)

    def add_group(self, title: str, layout_class: Type[QLayout]) -> "CollapsibleWidget":
        """Creates a new CollapsibleWidget as a child of the
        current widget.

        Args:
            title (str): Title of child CollapsibleWidget.
            layout_class (Type[QLayout]): Layout class of child CollapsibleWidget.

        Returns:
            CollapsibleWidget: The child CollapsibleWidget.
        """
        group = CollapsibleWidget(title, layout_class)
        self.content.addWidget(group)
        return group
