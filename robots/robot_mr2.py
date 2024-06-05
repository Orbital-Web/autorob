from kineval import Robot, Link, Joint
import numpy as np

# links
link_base = Link(name="base")
link_clavicle_right = Link(
    name="clavicle_right", _mesh=None
)  # TODO: define mesh for all links
link_clavicle_left = Link(name="clavicle_left")
link_shoulder_right = Link(name="shoulder_right")
link_upperarm_right = Link(name="upperarm_right")
link_forearm_right = Link(name="forearm_right")
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
    xyz=np.array([0.3, 0.4, 0.0], float),
    rpy=np.array([-np.pi / 2, 0.0, 0.0], float),
    axis=np.array([0.0, 0.0, -1.0], float),
)
joint_shoulder_right_yaw = Joint(
    name="shoulder_right_yaw",
    parent=link_clavicle_right,
    child=link_shoulder_right,
    xyz=np.array([0.0, -0.15, 0.85], float),
    rpy=np.array([np.pi / 2, 0.0, 0.0], float),
    axis=np.array([0.0, 0.707, 0.707], float),
)
joint_upperarm_right_pitch = Joint(
    name="upperarm_right_pitch",
    parent=link_shoulder_right,
    child=link_upperarm_right,
    xyz=np.array([0.0, 0.0, 0.7], float),
    rpy=np.array([0.0, 0.0, 0.0], float),
    axis=np.array([0.0, 1.0, 0.0], float),
)
joint_forearm_right_yaw = Joint(
    name="forearm_right_yaw",
    parent=link_upperarm_right,
    child=link_forearm_right,
    xyz=np.array([0.0, 0.0, 0.7], float),
    rpy=np.array([0.0, 0.0, 0.0], float),
    axis=np.array([1.0, 0.0, 0.0], float),
)
joint_clavicle_left_roll = Joint(
    name="clavicle_left_roll",
    parent=link_base,
    child=link_clavicle_left,
    xyz=np.array([-0.3, 0.4, 0.0], float),
    rpy=np.array([-np.pi / 2, 0.0, 0.0], float),
    axis=np.array([0.0, 0.0, 1.0], float),
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
