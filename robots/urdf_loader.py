from kineval import Robot, Link, Joint, Sphere
from scipy.spatial.transform import Rotation as R
import urchin
import trimesh
import pyvista as pv


def FromURDF(urdf_filename: str) -> Robot:
    """Creates a Robot from a urdf file.

    Args:
        urdf_filename (str): File to load from.

    Returns:
        Robot: The generated robot.
    """
    urdf_robot = urchin.URDF.load(urdf_filename)

    # create links
    link_names: dict[str, Link] = {}
    for link in urdf_robot.links:
        # create link geometry (either from mesh or an invisible one)
        if link.visuals and link.visuals[0].geometry.meshes:
            link_trimesh = link.visuals[0].geometry.meshes[0]
            # ignore textures
            if hasattr(link_trimesh, "visual"):
                link_trimesh.visual = trimesh.visual.ColorVisuals(link_trimesh)
            link_mesh = pv.wrap(link_trimesh)
            link_geom = pv.Actor(pv.DataSetMapper(link_mesh))
        else:
            link_geom = Sphere([0.0, 0.0, 0.0], 0)
        link_names[link.name] = Link(link.name, link_geom)

    # create joints
    joint_types = {
        "continuous": Joint.JointType.CONTINUOUS,
        "revolute": Joint.JointType.REVOLUTE,
        "prismatic": Joint.JointType.PRISMATIC,
    }
    joints = []
    for joint in urdf_robot.joints:
        joint_parent = link_names.get(joint.parent, None)
        joint_child = link_names.get(joint.child, None)
        # only create joint if we have both parent and child links
        if joint_parent and joint_child:
            joint_type = joint_types.get(joint.joint_type, Joint.JointType.FIXED)
            joint_xyz = joint.origin[0:3, 3]
            joint_rpy = R.from_matrix(joint.origin[0:3, 0:3]).as_euler("XYZ")
            joint_limit = None
            if joint_type in (Joint.JointType.REVOLUTE, Joint.JointType.PRISMATIC):
                joint_limit = [joint.limit.lower, joint.limit.upper]
            joints.append(
                Joint(
                    name=joint.name,
                    parent=joint_parent,
                    child=joint_child,
                    type=joint_type,
                    xyz=joint_xyz,
                    rpy=joint_rpy,
                    axis=joint.axis,
                    limits=joint_limit,
                )
            )

    return Robot(
        name=urdf_robot.name,
        base=link_names[urdf_robot.base_link.name],
        endeffector=link_names[urdf_robot.end_links[0].name],
        links=list(link_names.values()),
        joints=joints,
    )
