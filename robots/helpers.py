from kineval import Vec3
from scipy.spatial.transform import Rotation as R
import numpy as np
import pyvista as pv


def transform_mesh(mesh: pv.DataSet, xyz: Vec3 = None, rpy: Vec3 = None) -> pv.DataSet:
    """Transforms a mesh.

    Args:
        mesh (pv.DataSet): Mesh to transform.
        xyz (Vec3, optional): xyz translation vector. Defaults to None.
        rpy (Vec3, optional): Rotation angle (in radians) about the xyz axis. Defaults to None.

    Returns:
        pv.DataSet: The transformed mesh.
    """
    # no transformation needed
    if not xyz and not rpy:
        return mesh

    transform = np.identity(4)
    if xyz:
        transform[0:3, 3] = np.array(xyz)
    if rpy:
        transform[0:3, 0:3] = R.from_euler("XYZ", np.array(rpy)).as_matrix()
    return mesh.transform(transform)


def Box(shape: Vec3, xyz: Vec3 = None, rpy: Vec3 = None) -> pv.Actor:
    """Creates a box centered at its center of mass.

    Args:
        shape (Vec3): The length of the box about the xyz axis.
        xyz (Vec3, optional): xyz translation vector. Defaults to None.
        rpy (Vec3, optional): Rotation angle (in radians) about the xyz axis. Defaults to None.

    Returns:
        pv.Actor: The generated box geometry.
    """
    # create mesh
    x, y, z = shape
    mesh = pv.Box([-x / 2.0, x / 2.0, -y / 2.0, y / 2.0, -z / 2.0, z / 2.0])
    mesh = transform_mesh(mesh, xyz, rpy)

    # create geometry
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    return geom


def Cylinder(
    direction: Vec3,
    radius: float,
    height: float,
    xyz: Vec3 = None,
    rpy: Vec3 = None,
) -> pv.Actor:
    """Creates a cylinder centered at its centroid.

    Args:
        direction (Vec3): Direction the cylinder extends towards.
        radius (float): Radius of cylinder.
        height (float): Height of cylinder.
        xyz (Vec3, optional): xyz translation vector. Defaults to None.
        rpy (Vec3, optional): Rotation angle (in radians) about the xyz axis. Defaults to None.

    Returns:
        pv.Actor: The generated cylinder geometry.
    """
    # ensure inputs are np arrays
    direction = np.array(direction)

    # create mesh
    mesh = pv.Cylinder(direction=direction, radius=radius, height=height)
    mesh = transform_mesh(mesh, xyz, rpy)

    # create geometry
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    return geom
