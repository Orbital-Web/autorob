from kineval import Robot, Link, Joint, Box
import numpy as np

# links
link_base = Link(name="base", geom=Box(shape=[1.0, 1.0, 0.4], origin=[0.0, 0.0, 0.2]))
link_clavicle_right = Link(
    name="clavicle_right", geom=Box(shape=[0.3, 1.0, 0.3], origin=[0.0, 0.5, 0.0])
)
link_clavicle_left = Link(
    name="clavicle_left", geom=Box(shape=[0.3, 1.0, 0.3], origin=[0.0, 0.5, 0.0])
)
link_shoulder_right = Link(
    name="shoulder_right", geom=Box(shape=[0.3, 0.7, 0.3], origin=[0.0, 0.35, 0.0])
)
link_upperarm_right = Link(
    name="upperarm_right", geom=Box(shape=[0.3, 0.7, 0.3], origin=[0.0, 0.35, 0.0])
)
link_forearm_right = Link(
    name="forearm_right", geom=Box(shape=[0.3, 0.5, 0.3], origin=[0.0, 0.25, 0.0])
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
    xyz=[-0.3, 0.0, 0.4],
    rpy=[np.pi / 2, 0.0, 0.0],
    axis=[0.0, 1.0, 0.0],
)
joint_shoulder_right_yaw = Joint(
    name="shoulder_right_yaw",
    parent=link_clavicle_right,
    child=link_shoulder_right,
    xyz=[0.0, 0.85, -0.15],
    rpy=[-np.pi / 2, 0.0, 0.0],
    axis=[0.0, 0.707, -0.707],
)
joint_upperarm_right_pitch = Joint(
    name="upperarm_right_pitch",
    parent=link_shoulder_right,
    child=link_upperarm_right,
    xyz=[0.0, 0.7, 0.0],
    rpy=[0.0, 0.0, 0.0],
    axis=[0.0, 0.0, -1.0],
)
joint_forearm_right_yaw = Joint(
    name="forearm_right_yaw",
    parent=link_upperarm_right,
    child=link_forearm_right,
    xyz=[0.0, 0.7, 0.0],
    rpy=[0.0, 0.0, 0.0],
    axis=[1.0, 0.0, 0.0],
)
joint_clavicle_left_roll = Joint(
    name="clavicle_left_roll",
    parent=link_base,
    child=link_clavicle_left,
    xyz=[0.3, 0.0, 0.4],
    rpy=[np.pi / 2, 0.0, 0.0],
    axis=[0.0, 1.0, 0.0],
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
    name="Mr. 2",
    base=link_base,
    endeffector=link_forearm_right,
    links=links,
    joints=joints,
)
