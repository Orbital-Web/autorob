from kineval import Robot, World, RobotConfiguration, Marker
from kineval.collision import IsPoseCollison
from pyvistaqt import QtInteractor
from enum import Enum
from typing import Literal
import numpy as np


class RRTNode:
    """A single node of an RRT tree."""

    def __init__(self, configuration: RobotConfiguration):
        # structure
        self.configuration: RobotConfiguration = configuration
        self.edges: list[RRTNode] = []
        # visual
        self.marker: Marker = None


class RRTInfo:
    """A struct for storing the RRT trees and other info."""

    class RRTState(Enum):
        WAITING = 0
        ITERATING = 1
        REACHED = 2
        TRAPPED = 3
        ADVANCED = 4

    def __init__(self, robot: Robot, world: World, plotter: QtInteractor):
        self.robot: Robot = robot
        self.world: World = world
        self.plotter: QtInteractor = plotter
        self.treeA: list[RRTNode] = []
        self.treeB: list[RRTNode] = []
        self.path: list[RRTNode] = []
        self.steps: int = 0
        self.status: RRTInfo.RRTState = RRTInfo.RRTState.WAITING
        self.stepsize: float = 1.0

    def addVertex(
        self, configuration: RobotConfiguration, tree: Literal["A", "B"]
    ) -> RRTNode:
        """Adds a new node to the RRT tree. Additionally adds a new marker
        to the world.

        Args:
            configuration (RobotConfiguration): The configuration of the new node.
            tree (Literal["A", "B"]): Whether to add the vertex to tree A or B.

        Raises:
            ValueError: If `tree` is not "A" or "B"

        Returns:
            RRTNode: The added node.
        """
        # add node
        node = RRTNode(configuration)
        if tree == "A":
            self.treeA.append(node)
        elif tree == "B":
            self.treeB.append(node)
        else:
            raise ValueError("Argument 'tree' must be either 'A' or 'B'.")

        # add marker
        node.marker = self.world.addMarker(
            [*configuration.base_position, 1.0], self.plotter
        )

        return node

    def addEdge(self, v1: RRTNode, v2: RRTNode):
        """Creates an edge between the two input nodes.
        Assumes there isn't an edge between the two nodes yet.

        Args:
            v1 (RRTNode): One end of the edge.
            v2 (RRTNode): Other end of the edge.
        """
        v1.edges.append(v2)
        v2.edges.append(v1)

    def swapTrees(self):
        """Swaps the two RRT trees so that treeA points to treeB
        and vice versa."""
        self.treeA, self.treeB = self.treeB, self.treeA


def ResetRRT(
    robot: Robot, world: World, plotter: QtInteractor, goal_config: RobotConfiguration
) -> RRTInfo:
    """Resets and initializes a new RRT search."""
    # NOTE: This function is already written for you
    qstart = RobotConfiguration(robot)
    qgoal = goal_config
    # create new RRTInfo
    info = RRTInfo(robot, world, plotter)
    info.addVertex(qstart, "A")
    info.addVertex(qgoal, "B")
    return info


def StepRRT(info: RRTInfo):
    """Runs a single iteration of RRT-connect.

    Args:
        info (RRTInfo): Variables and info related to RRT.
    """
    # TODO: YOUR CODE HERE
    # Implement a single iteration of RRT-connect.
    # Make sure to set info.status to REACHED once a path is found.
    # You may want to write additional helper functions.

    # FIXME: remove instructor solution below
    qrand = RandomConfig(info)
    status, qnew = ExtendRRT(info, qrand)
    if (
        status != RRTInfo.RRTState.TRAPPED
        and ConnectRRT(info, qnew) == RRTInfo.RRTState.REACHED
    ):
        GeneratePathRRT(info)
        info.status = RRTInfo.RRTState.REACHED

    info.swapTrees()
    info.steps += 1
    info.status = RRTInfo.RRTState.ITERATING


# TODO: YOUR CODE HERE
# Implement other functions that you think are necessary, such as
# ExtendRRT, ConnectRRT, GeneratePathRRT, RandomConfig, FindNearest, ConfigDistance


# FIXME: remove instructor solution below
def ExtendRRT(info: RRTInfo, qrand: RobotConfiguration) -> RRTInfo.RRTState:
    node_near, dnear = FindNearest(info.treeA, qrand)
    # create new config towards qrand
    if dnear > info.stepsize:
        qnear_vec = node_near.configuration.asVec()
        qrand_vec = qrand.asVec()
        # move step_size towards qrand from qnear
        qnew = RobotConfiguration(info.robot).fromVec(
            qnear_vec + (qrand_vec - qnear_vec) * info.stepsize / dnear
        )
    else:
        qnew = qrand

    if IsPoseCollison(info.robot, qnew, info.world):
        return RRTInfo.RRTState.TRAPPED, qnew

    # add new node
    node_new = info.addVertex(qnew, "A")
    info.addEdge(node_new, node_near)

    if qnew == qrand:
        return RRTInfo.RRTState.REACHED, qnew
    return RRTInfo.RRTState.ADVANCED, qnew


def ConnectRRT(info: RRTInfo, qnew: RobotConfiguration):
    status = ExtendRRT(info, qnew)
    while status == RRTInfo.RRTState.ADVANCED:
        status = ExtendRRT(info, qnew)
    return status


def GeneratePathRRT(info: RRTInfo):
    pass


def RandomConfig(info: RRTInfo) -> RobotConfiguration:
    # create a config for the robot
    qrand = RobotConfiguration(info.robot)
    # randomize base position and rotation
    x0, x1 = info.world.bounds[0, :]
    y0, y1 = info.world.bounds[1, :]
    qrand.base_position = np.random.rand(2) * [x1 - x0, y1 - y0] + [x0, y0]
    qrand.base_rotation = 2 * np.pi * np.random.rand() - np.pi
    # randomize joint rotations
    for joint_name in qrand:
        qrand.joint_configs[joint_name] = 2 * np.pi * np.random.rand() - np.pi
    return qrand


def FindNearest(
    tree: list[RRTNode], configuration: RobotConfiguration
) -> tuple[RRTNode, float]:
    qnear = tree[0]
    dnear = float("inf")

    # search for closest node
    for node in tree:
        dnode = ConfigDistance(configuration, node.configuration)
        if dnode < dnear:
            dnear = dnode
            qnear = node

    # return closest node and its distance
    return qnear, dnear


def ConfigDistance(config1: RobotConfiguration, config2: RobotConfiguration) -> float:
    # return the distance of these vectors
    return np.linalg.norm(config1.asVec() - config2.asVec())
