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
        self.parent: RRTNode = None
        # visual
        self.marker: Marker = None


class RRTInfo:
    """A struct for storing the RRT trees and other info."""

    class RRTState(Enum):
        ITERATING = 0
        REACHED = 1
        TRAPPED = 2
        ADVANCED = 3

    def __init__(
        self,
        robot: Robot,
        world: World,
        plotter: QtInteractor,
        start: RobotConfiguration,
        goal: RobotConfiguration,
    ):
        self.robot: Robot = robot
        self.world: World = world
        self.plotter: QtInteractor = plotter
        self.treeA: list[RRTNode] = []
        self.treeB: list[RRTNode] = []
        self.path: list[RRTNode] = []
        self.start: RRTNode = self.addVertex(start, "A")
        self.goal: RRTNode = self.addVertex(goal, "B")
        self.steps: int = 0
        self.status: RRTInfo.RRTState = RRTInfo.RRTState.ITERATING
        self.stepsize: float = 0.5

    def addVertex(
        self, configuration: RobotConfiguration, tree: Literal["A", "B"]
    ) -> RRTNode:
        """Adds a new node to the RRT tree. Additionally adds a new marker
        to the world.

        Args:
            configuration (RobotConfiguration): The configuration of the new node.
            tree (Literal["A", "B"]): Whether to add the vertex to tree A or B.

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

    def addEdge(self, node_from: RRTNode, node_to: RRTNode):
        """Creates a directed edge from node_from to node_to.

        Args:
            node_from (RRTNode): Parent node.
            node_to (RRTNode): Child node.
        """
        node_to.parent = node_from

    def swapTrees(self):
        """Swaps the two RRT trees so that treeA points to treeB
        and vice versa."""
        self.treeA, self.treeB = self.treeB, self.treeA


def StepRRT(info: RRTInfo):
    """Runs a single iteration of RRT-connect.

    Args:
        info (RRTInfo): Variables and info related to RRT.
    """
    # NOTE: Do NOT remove the following lines of code
    if info is None or info.status != RRTInfo.RRTState.ITERATING:
        return

    # TODO: YOUR CODE HERE
    # Implement a single iteration of RRT-connect.
    # You should set info.status to REACHED once a path is found.
    # You may want to write additional helper functions.

    # FIXME: remove instructor solution below
    qrand = RandomConfig(info)
    status, qnew = ExtendRRT(info, qrand, "A")
    if (
        status != RRTInfo.RRTState.TRAPPED
        and ConnectRRT(info, qnew, "B") == RRTInfo.RRTState.REACHED
    ):
        GeneratePathRRT(info)
        info.status = RRTInfo.RRTState.REACHED

    info.swapTrees()
    info.steps += 1


# TODO: YOUR CODE HERE
# Implement other functions that you think are necessary, such as
# ExtendRRT, ConnectRRT, GeneratePathRRT, RandomConfig, FindNearest


# FIXME: remove instructor solution below
def ExtendRRT(
    info: RRTInfo, qrand: RobotConfiguration, tree: Literal["A", "B"]
) -> tuple[RRTInfo.RRTState, RRTNode]:
    node_near, dnear = FindNearest(info.treeA if tree == "A" else info.treeB, qrand)

    # create new config towards qrand
    if dnear > info.stepsize:
        qnear_vec = node_near.configuration.asVec()
        qrand_vec = qrand.asVec()
        # move step_size towards qrand from qnear
        qnew = RobotConfiguration(info.robot).fromVec(
            qnear_vec + (qrand_vec - qnear_vec) * info.stepsize / dnear
        )
    else:
        node_new = info.addVertex(qrand, tree)
        info.addEdge(node_near, node_new)
        return RRTInfo.RRTState.REACHED, qrand

    if IsPoseCollison(info.robot, qnew, info.world):
        return RRTInfo.RRTState.TRAPPED, qnew

    node_new = info.addVertex(qnew, tree)
    info.addEdge(node_near, node_new)
    return RRTInfo.RRTState.ADVANCED, qnew


def ConnectRRT(
    info: RRTInfo, qnew: RobotConfiguration, tree: Literal["A", "B"]
) -> RRTInfo.RRTState:
    status, _ = ExtendRRT(info, qnew, tree)
    while status == RRTInfo.RRTState.ADVANCED:
        status, _ = ExtendRRT(info, qnew, tree)
    return status


def GeneratePathRRT(info: RRTInfo):
    # make sure treeA contains start
    if info.treeA[0] != info.start:
        info.swapTrees()

    # get path from node to start
    node = info.treeA[-1]
    while node is not None:
        node.marker.setColor([1, 0, 0])
        info.path.insert(0, node)
        node = node.parent

    # add path from node to goal
    node = info.treeB[-1].parent
    while node is not None:
        node.marker.setColor([1, 0, 0])
        info.path.append(node)
        node = node.parent


def RandomConfig(info: RRTInfo) -> RobotConfiguration:
    # create a config for the robot
    qrand = RobotConfiguration(info.robot)
    # randomize base position and rotation
    x0, x1 = info.world.bounds[0, :]
    y0, y1 = info.world.bounds[1, :]
    qrand.base_position = np.random.rand(2) * [x1 - x0, y1 - y0] + [x0, y0]
    qrand.base_rotation = 2 * np.pi * np.random.rand() - np.pi
    # randomize joint rotations
    for joint_name in qrand.joint_configs:
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
