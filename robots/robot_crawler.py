from kineval import Robot, Link, Joint
from robots import Box
import numpy as np

# links
link_base = Link(name="base", geom=Box(shape=[1.0, 2.3, 0.4], xyz=[0.0, 0.0, 0]))
link_legs = []
for i in range(8):
    link_i_upper = Link(
        name=f"leg{i+1}_upper", geom=Box(shape=[0.3, 0.3, 0.3], xyz=[0.0, 0.15, 0.0])
    )
    link_i_middle = Link(
        name=f"leg{i+1}_middle", geom=Box(shape=[0.3, 0.6, 0.3], xyz=[0.0, 0.3, 0.0])
    )
    link_i_lower = Link(
        name=f"leg{i+1}_lower", geom=Box(shape=[0.3, 1.0, 0.3], xyz=[0.0, 0.5, 0.0])
    )
    link_legs.extend([link_i_upper, link_i_middle, link_i_lower])
links = [link_base, *link_legs]

# joints
joints = []
for i in range(8):
    sign1_i = -1 if i & 2 else 1  # 1  1 -1 -1 ...
    sign2_i = -1 if i % 2 else 1  # 1 -1  1 -1 ...
    sign3_i = 0.9 if i < 4 else 0.3
    link_i_upper = link_legs[3 * i]
    link_i_middle = link_legs[3 * i + 1]
    link_i_lower = link_legs[3 * i + 2]

    leg_i_hip = Joint(
        name=f"leg{i+1}_hip",
        parent=link_base,
        child=link_i_upper,
        xyz=[sign1_i * -0.3, sign2_i * sign3_i, 0.0],
        rpy=[0.0, 0.0, sign1_i * np.pi / 2],
        axis=[0.0, 0.0, 1.0],
    )
    leg_i_knee = Joint(
        name=f"leg{i+1}_knee",
        parent=link_i_upper,
        child=link_i_middle,
        xyz=[0.0, 0.4, 0.0],
        rpy=[np.pi / 4, 0.0, 0.0],
        axis=[1.0, 0.0, 0.0],
    )
    leg_i_ankle = Joint(
        name=f"leg{i+1}_ankle",
        parent=link_i_middle,
        child=link_i_lower,
        xyz=[0.0, 0.6, 0.0],
        rpy=[-np.pi / 2, 0.0, 0.0],
        axis=[1.0, 0.0, 0.0],
    )
    joints.extend([leg_i_hip, leg_i_knee, leg_i_ankle])

# robot definiton
robot = Robot(
    name="crawler",
    base=link_base,
    endeffector=joints[2],
    links=links,
    joints=joints,
)
