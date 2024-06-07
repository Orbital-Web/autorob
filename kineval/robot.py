from kineval import Vec2, Vec3, Mat4D
import numpy as np
import pyvista as pv
from enum import Enum


def set_using_kwargs(self, kwargs: dict, exclude: set[str] = None) -> None:
    """Sets self.{key} to {var} for {key, var} in `kwargs`.
    Raises warning if {key} is not an attribute of `self`
    or is in `exclude`.

    Args:
        self: object to set the attributes.
        kwargs (dict): attribute names and their desired values.
        exclude (set, optional): attributes to exclude.
    """
    if not kwargs:
        return

    # get set of modifiable attributes
    allowed_keys = set(self.__dict__.keys())
    if exclude:
        allowed_keys -= exclude

    # update attributes
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
        self.name: str = ""  # name of link
        self.parent: Joint = None  # parent joint
        self.children: list[Joint] = []  # list of children joints
        # visual
        self.geom: pv.Actor = None  # rendered geometry of link
        set_using_kwargs(self, kwargs)


class Joint:
    """A joint class for the robot."""

    class JointType(Enum):
        CONTINUOUS = 0  # rotates around axis, no joint limit
        REVOLUTE = 1  # rotates around axis, has joint limits
        PRISMATIC = 2  # slides along axis, has joint limits

    def __init__(self, **kwargs) -> None:
        # structure
        self.name: str = ""  # name of joint
        self.parent: Link = None  # parent link
        self.child: Link = None  # child link
        self.type: Joint.JointType = Joint.JointType.CONTINUOUS  # type of joint
        # static configurations
        self.xyz: Vec3 = np.zeros((3), float)  # starting position
        self.rpy: Vec3 = np.zeros((3), float)  # starting rotation
        self.axis: Vec3 = np.array([1, 0, 0], float)  # axis the joint moves around
        self.limits: Vec2 | None = None  # [min, max] theta values or None for no limits
        # dynamic configurations
        self.theta: float = 0.0  # configuration of joint
        self.transform: Mat4D = np.identity(4, float)  # homogenous transform matrix
        # visual
        self.geom: pv.Actor = None  # rendered geometry of joint
        self.axis_geom: pv.Actor = None  # rendered geometry of joint axis
        set_using_kwargs(self, kwargs, exclude={"geom", "axis_geom"})


class Robot:
    """A bare-minimum class for representing a robot."""

    def __init__(self, **kwargs) -> None:
        # structure
        self.name: str = ""  # name of robot
        self.base: Link = None  # base link
        self.endeffector: Link = None  # endeffector link
        self.links: list[Link] = []  # links in the robot
        self.joints: list[Joint] = []  # joints in the robot
        # dynamic configurations
        self.xyz: Vec3 = np.zeros((3), float)  # base position
        self.rpy: Vec3 = np.zeros((3), float)  # base rotation
        self.transform: Mat4D = np.identity(4, float)  # homogenous transform matrix
        self.facing: Vec3 = np.array([1, 0, 0], float)  # unit vector of front direction
        # ui
        self.selected: Joint = None  # currently selected joint on UI
        set_using_kwargs(self, kwargs, exclude={"facing", "selected"})
