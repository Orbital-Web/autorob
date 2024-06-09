from kineval import Vec2, Vec3, Mat4D
import numpy as np
import pyvista as pv
from enum import Enum


class Link:
    """A link class for the robot."""

    def __init__(self, name: str, geom: pv.Actor) -> None:
        # structure
        self.name: str = name
        self.parent: Joint = None  # parent joint
        self.children: list[Joint] = []  # list of children joints
        # visual
        self.geom: pv.Actor = geom  # rendered geometry of link


class Joint:
    """A joint class for the robot."""

    class JointType(Enum):
        CONTINUOUS = 0  # rotates around axis, no joint limit
        REVOLUTE = 1  # rotates around axis, has joint limits
        PRISMATIC = 2  # slides along axis, has joint limits

    def __init__(
        self,
        name: str,
        parent: Link,
        child: Link,
        type: JointType = JointType.CONTINUOUS,
        xyz: Vec3 = None,
        rpy: Vec3 = None,
        axis: Vec3 = None,
        limits: Vec2 | None = None,
    ) -> None:
        # structure
        self.name: str = name  # name of joint
        self.parent: Link = parent  # parent link
        self.child: Link = child  # child link
        self.type: Joint.JointType = type  # type of joint
        # static configurations
        self.xyz: Vec3 = (
            np.zeros((3), float) if xyz is None else xyz
        )  # starting position
        self.rpy: Vec3 = (
            np.zeros((3), float) if rpy is None else rpy
        )  # starting rotation
        self.axis: Vec3 = (
            np.array([1, 0, 0], float) if axis is None else axis
        )  # joint axis
        self.limits: Vec2 | None = limits  # [min, max] of theta or None for no limits
        # dynamic configurations
        self.theta: float = 0.0  # configuration of joint
        self.transform: Mat4D = np.identity(4, float)  # homogenous transform matrix
        # visual
        self.geom: pv.Actor = None  # rendered geometry of joint
        self.axis_geom: pv.Actor = None  # rendered geometry of joint axis


class Robot:
    """A bare-minimum class for representing a robot."""

    def __init__(
        self,
        name: str,
        base: Link,
        endeffector: Link,
        links: list[Link],
        joints: list[Joint],
        xyz: Vec3 = None,
        rpy: Vec3 = None,
    ) -> None:
        # structure
        self.name: str = name  # name of robot
        self.base: Link = base  # base link
        self.endeffector: Link = endeffector  # endeffector link
        self.links: list[Link] = links  # links in the robot
        self.joints: list[Joint] = joints  # joints in the robot
        # dynamic configurations
        self.xyz: Vec3 = np.zeros((3), float) if xyz is None else xyz  # base position
        self.rpy: Vec3 = np.zeros((3), float) if rpy is None else rpy  # base rotation
        self.transform: Mat4D = np.identity(4, float)  # homogenous transform matrix
        self.facing: Vec3 = np.array([1, 0, 0], float)  # unit vector of front direction
        # visual
        self.selected: Joint = joints[0]  # currently selected joint on UI