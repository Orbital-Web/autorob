from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGroupBox,
    QToolButton,
    QFrame,
    QSpacerItem,
    QSizePolicy,
    QLayout,
)
from PyQt5.QtCore import Qt
from typing import Type


class CollapsibleWidget(QGroupBox):
    """A widget who's content can be collapsed or expanded
    by clicking on its title. It's layout can be accessed for
    formatting and adding sub-widgets through the `content`
    attribute.
    """

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
        self.toggle_button = QToolButton(text=title, checkable=True, checked=True)
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
