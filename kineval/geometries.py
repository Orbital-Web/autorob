from kineval import Vec3, Vec2
from scipy.spatial.transform import Rotation as R
import numpy as np
import pyvista as pv


def transform_mesh(mesh: pv.DataSet, xyz: Vec3 = None, rpy: Vec3 = None) -> pv.DataSet:
    """Transforms a mesh.

    Args:
        mesh (pv.DataSet): Mesh to transform.
        xyz (Vec3, optional): xyz translation vector. Defaults to None.
        rpy (Vec3, optional): Rotation angle of the mesh (in radians) about the xyz axes. Defaults to None.

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


def Box(origin: Vec3, shape: Vec3, rpy: Vec3 = None) -> pv.Actor:
    """Creates a box geometry.

    Args:
        origin (Vec3): Center of the box.
        shape (Vec3): Length of the box along the xyz axes.
        rpy (Vec3, optional): Rotation angle (in radians) of the box about the xyz axes. Defaults to None.

    Returns:
        pv.Actor: The generated box geometry.
    """
    # create mesh
    x, y, z = shape
    mesh = pv.Box([-x / 2.0, x / 2.0, -y / 2.0, y / 2.0, -z / 2.0, z / 2.0])
    mesh = transform_mesh(mesh, xyz=origin, rpy=rpy)

    # create geometry
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    return geom


def Cylinder(
    origin: Vec3,
    direction: Vec3,
    radius: float,
    height: float,
) -> pv.Actor:
    """Creates a cylinder geometry.

    Args:
        origin (Vec3): Centroid of the cylinder.
        direction (Vec3): Direction the cylinder extends towards.
        radius (float): Radius of cylinder.
        height (float): Height of cylinder.

    Returns:
        pv.Actor: The generated cylinder geometry.
    """
    # ensure inputs are np arrays
    direction = np.array(direction)

    # create mesh
    mesh = pv.Cylinder(direction=direction, radius=radius, height=height)
    mesh = transform_mesh(mesh, xyz=origin)

    # create geometry
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    return geom


def Line(origin: Vec3, direction: Vec3, length: float, thickness: int = 1) -> pv.Actor:
    """Creates a line geometry.

    Args:
        origin (Vec3): Starting point of line.
        direction (Vec3): Direction of the line.
        length (float): Length of the line.
        thickness (int): Thickness of the line.

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
    """Creates a plane geometry.

    Args:
        origin (Vec3): Center of the plane.
        normal (Vec3): Normal vector of the plane.
        size (Vec2): Vertical and horizontal length of the plane.

    Returns:
        pv.Actor: The generated plane geometry.
    """
    # ensure inputs are np arrays
    origin = np.array(origin)
    normal = np.array(normal)

    # create mesh
    mesh = pv.Plane(origin, normal, *size, *np.int32(size))
    mesh.point_data.clear()

    # create geometry
    geom = pv.Actor(mapper=pv.DataSetMapper(mesh))
    geom.prop.SetEdgeVisibility(True)
    return geom
