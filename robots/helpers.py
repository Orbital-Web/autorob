from kineval import Vec3, Vec2
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


def Line(origin: Vec3, direction: Vec3, length: float, thickness: int = 1) -> pv.Actor:
    """Creates a line centered at `origin` and extending towards
    `direction` for length `length`.

    Args:
        origin (Vec3): Origin of line.
        direction (Vec3): Direction of line.
        length (float): Length of line.
        thickness (int): Thickness of line.

    Returns:
        pv.Actor: The generated line geometry.
    """
    # ensure inputs are np arrays
    origin = np.array(origin)
    direction = np.array(direction)

    # create mesh
    mesh = pv.Line(origin, origin + length * direction)

    # create geometry
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    geom.prop.SetLineWidth(thickness)
    return geom


def Plane(origin: Vec3, normal: Vec3, size: Vec2) -> pv.Actor:
    """Creates a plane centered at `origin` with normal facing
    towards `normal`.

    Args:
        origin (Vec3): Origin of plane.
        normal (Vec3): Normal vector of line.
        size (Vec2): x and y size of plane.

    Returns:
        pv.Actor: The generated plane geometry.
    """
    # ensure inputs are np arrays
    origin = np.array(origin)
    normal = np.array(normal)

    # create mesh
    mesh = pv.Plane(origin, normal, *size)

    # create geometry
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    return geom
