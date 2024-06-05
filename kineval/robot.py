import numpy as np

from enum import Enum
from .types import Vec2, Vec3, Mat4D
from typing import Any


def set_using_kwargs(self, kwargs: dict):
    """
    Sets self.{key} to {var} for {key, var} in `kwargs`.
    Raises warning if {key} is not an attribute of `self`.
    """
    if not kwargs:
        return

    allowed_keys = set(self.__dict__.keys())
    self.__dict__.update(
        (key, val) for key, val in kwargs.items() if key in allowed_keys
    )
    # raise warnings
    rejected_keys = set(kwargs.keys()) - allowed_keys
    if rejected_keys:
        print(
            f"WARNING. The following key(s) were ignored when constructing '{type(self).__name__}': {rejected_keys}"
        )


class Link:
    """A link class for the robot."""

    def __init__(self, **kwargs) -> None:
        # structure
        self.name: str = ""
        self.parent: Joint = None
        self.children: list[Joint] = []
        # static configurations
        self.xyz: Vec3 = np.zeros((3), float)
        self.rpy: Vec3 = np.zeros((3), float)
        # visual
        self._mesh = None  # TODO: figure out which module to use
        set_using_kwargs(self, kwargs)


class Joint:
    """A joint class for the robot."""

    class JointType(Enum):
        CONTINUOUS = 0
        REVOLUTE = 1
        PRISMATIC = 2

    def __init__(self, **kwargs) -> None:
        # structure
        self.name: str = ""
        self.parent: Link = None
        self.child: Link = None
        self.type: Joint.JointType = Joint.JointType.CONTINUOUS
        # static configurations
        self.xyz: Vec3 = np.zeros((3), float)
        self.rpy: Vec3 = np.zeros((3), float)
        self.axis: Vec3 = np.array([1, 0, 0], float)
        self.limits: Vec2 | None = None
        # dynamic configurations
        self.theta: float = 0.0
        self.transform: Mat4D = np.identity(4, float)
        set_using_kwargs(self, kwargs)


class Robot:
    """A bare-minimum class for representing a robot."""

    def __init__(self, **kwargs) -> None:
        # structure
        self.base: Link = None
        self.endeffector: Link = None
        self.links: list[Link] = []  # TODO: maybe use a dict, idk yet
        self.joints: list[Joint] = []  # TODO: maybe use a dict, idk yet
        # dynamic configurations
        self.xyz: Vec3 = np.zeros((3), float)
        self.rpy: Vec3 = np.zeros((3), float)
        set_using_kwargs(self, kwargs)

    # FIXME: move following function to a manager class that takes in a robot
    # and renders it, so students can't accidentally mess this up
    # def _render(self, *args) -> None:
    #     """
    #     Renders each link and joint.
    #     Joints are drawn using `transform` and `axis`.
    #     Links are drawn using `_mesh`, `xyz, `rpy`, and the parent
    #     joint's `transform`.
    #     """
    #     # TODO: write this function when we figure out which modules to use
    #     # will probably get called in the main loop, not called by students
    #     # might take in additional args like canvas, color, joint sizes, etc.
    #     # link xyz and rpy are used to offset where the mesh is drawn from the
    #     # joint position in the world frame (in case the mesh itself is offset)
    #     pass

    # TODO: FK and IK might go in here, or more likely would be a function a student
    # implements in another file which takes a robot as an argument and traverses
    # it, modifying each joint's `transform`
