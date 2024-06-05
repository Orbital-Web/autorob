from kineval import Robot, Link, Joint
from .helpers import Box
import numpy as np

# links
link_base = Link(name="base", geom=Box(shape=[1.0, 1.0, 0.4], xyz=[0.0, 0.0, 0.2]))
link_clavicle_right = Link(
    name="clavicle_right", geom=Box(shape=[0.3, 1.0, 0.3], xyz=[0.0, 0.5, 0.0])
)
link_clavicle_left = Link(
    name="clavicle_left", geom=Box(shape=[0.3, 1.0, 0.3], xyz=[0.0, 0.5, 0.0])
)
link_shoulder_right = Link(
    name="shoulder_right", geom=Box(shape=[0.3, 0.7, 0.3], xyz=[0.0, 0.35, 0.0])
)
link_upperarm_right = Link(
    name="upperarm_right", geom=Box(shape=[0.3, 0.7, 0.3], xyz=[0.0, 0.35, 0.0])
)
link_forearm_right = Link(
    name="forearm_right", geom=Box(shape=[0.3, 0.5, 0.3], xyz=[0.0, 0.25, 0.0])
)
links = [
    link_base,
    link_clavicle_right,
    link_clavicle_left,
    link_shoulder_right,
    link_upperarm_right,
    link_forearm_right,
]

# joints
joint_clavicle_right_yaw = Joint(
    name="clavicle_right_yaw",
    parent=link_base,
    child=link_clavicle_right,
    xyz=np.array([0.3, 0.0, 0.4], float),
    rpy=np.array([np.pi / 2, 0.0, 0.0], float),
    axis=np.array([0.0, -1.0, 0.0], float),
)
joint_shoulder_right_yaw = Joint(
    name="shoulder_right_yaw",
    parent=link_clavicle_right,
    child=link_shoulder_right,
    xyz=np.array([0.0, 0.85, 0.15], float),
    rpy=np.array([np.pi / 2, 0.0, 0.0], float),
    axis=np.array([0.0, 0.707, -0.707], float),
)
joint_upperarm_right_pitch = Joint(
    name="upperarm_right_pitch",
    parent=link_shoulder_right,
    child=link_upperarm_right,
    xyz=np.array([0.0, 0.7, 0.0], float),
    rpy=np.array([0.0, 0.0, 0.0], float),
    axis=np.array([0.0, 0.0, -1.0], float),
)
joint_forearm_right_yaw = Joint(
    name="forearm_right_yaw",
    parent=link_upperarm_right,
    child=link_forearm_right,
    xyz=np.array([0.0, 0.7, 0.0], float),
    rpy=np.array([0.0, 0.0, 0.0], float),
    axis=np.array([1.0, 0.0, 0.0], float),
)
joint_clavicle_left_roll = Joint(
    name="clavicle_left_roll",
    parent=link_base,
    child=link_clavicle_left,
    xyz=np.array([-0.3, 0.0, 0.4], float),
    rpy=np.array([np.pi / 2, 0.0, 0.0], float),
    axis=np.array([0.0, 1.0, 0.0], float),
)
joints = [
    joint_clavicle_right_yaw,
    joint_shoulder_right_yaw,
    joint_upperarm_right_pitch,
    joint_forearm_right_yaw,
    joint_clavicle_left_roll,
]

# robot definiton
robot = Robot(
    base=link_base,
    endeffector=link_forearm_right,
    links=links,
    joints=joints,
    xyz=np.zeros((3), float),
    rpy=np.zeros((3), float),
)

# FIXME: this should be done by the students for FK project

for joint in robot.joints:
    parent = joint.parent
    parent.children.append(joint)

    child = joint.child
    child.parent = joint

from scipy.spatial.transform import Rotation as R


def traverse_link(mstack, link: Link):
    for joint in link.children:
        traverse_joint(np.copy(mstack), joint)


def traverse_joint(mstack, joint: Joint):
    q = np.identity(4)
    quat = [*(np.sin(joint.theta / 2) * joint.axis), np.cos(joint.theta / 2)]
    q[0:3, 0:3] = R.from_quat(quat).as_matrix()

    m = np.identity(4)
    m[0:3, 0:3] = R.from_euler("XYZ", np.array(joint.rpy)).as_matrix()
    m[0:3, 3] = joint.xyz
    m = m @ q
    mstack = mstack @ m
    joint.transform = mstack
    traverse_link(mstack, joint.child)


mstack = np.identity(4)
mstack[0:3, 0:3] = R.from_euler("XYZ", np.array(robot.rpy)).as_matrix()
mstack[0:3, 3] = robot.xyz
robot.transform = mstack
traverse_link(mstack, robot.base)
