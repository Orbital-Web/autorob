from scipy.spatial.transform import Rotation as R
import numpy as np
import pyvista as pv

from kineval import Vec3


def transform_mesh(mesh: pv.DataSet, xyz: Vec3 = None, rpy: Vec3 = None) -> pv.DataSet:
    """
    Transforms mesh by `xyz` and `rpy`, returning the
    transformed mesh.
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
    """
    Creates a box geom.
    By default, the box's origin is at its center of mass.
    The origin can be shifted with `xyz`, and rotated with `rpy`.
    """
    x, y, z = shape

    mesh = pv.Box([-x / 2.0, x / 2.0, -y / 2.0, y / 2.0, -z / 2.0, z / 2.0])
    mesh = transform_mesh(mesh, xyz, rpy)
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    return geom


def Cylinder(
    direction: Vec3, radius: float, height: float, xyz: Vec3 = None, rpy: Vec3 = None
) -> pv.Actor:
    """
    Creates a cylinder geom.
    By default, the cylinder is centered at its center of mass.
    The origin can be shifted with `xyz`, and rotated with `rpy`.
    """
    # ensure inputs are np arrays
    direction = np.array(direction)

    mesh = pv.Cylinder(direction=direction, radius=radius, height=height)
    mesh = transform_mesh(mesh, xyz, rpy)
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    return geom
