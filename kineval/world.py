from kineval import Plane, Vec4, Vec3, Vec2, Mat2, Sphere
from pyvistaqt import QtInteractor
import numpy as np
import pyvista as pv


class Obstacle:
    """A basic definition of a spherical obstacle."""

    def __init__(self, origin: Vec3, radius: float):
        # structure
        self.origin: Vec3 = np.array(origin, float)  # center of obstalce
        self.radius: float = radius  # radius of obstacle
        self.origin_homogeneous: Vec4 = np.array(
            [*origin, 1], float
        )  # homogeneous obstacle center
        self.geom: pv.Actor = Sphere(origin, radius)  # rendered geometry of obstacle


class Marker:
    """An object to mark a robot configuration in the world."""

    def __init__(self, origin: Vec3):
        # structure
        self.origin: Vec3 = np.array(origin)  # position of marker
        # visual
        self.geom: pv.Actor = Sphere(self.origin, 0.05)

    def setColor(self, color: Vec3):
        self.geom.prop.SetColor(*color)


class World:
    """A class for holding all the obstacles, terrain, etc. that are in the world."""

    def __init__(self, name: str, obstacles: list[Obstacle] = None, size: Vec2 = None):
        self.name: str = name  # name of world
        self.obstacles: list[Obstacle] = (
            [] if obstacles is None else obstacles
        )  # list of obstacles
        self.markers: list[Marker] = []  # list of markers
        self.size: Vec2 = (
            np.array([10.0, 10.0], float) if size is None else np.array(size, float)
        )  # x and y length of the world
        self.bounds: Mat2 = np.array(
            [
                [-self.size[0] / 2, self.size[0] / 2],
                [-self.size[1] / 2, self.size[1] / 2],
            ]
        )  # x and y bounds of the world
        self.terrain: pv.Actor = Plane(
            origin=[0.0, 0.0, -0.01], normal=[0.0, 0.0, 1.0], size=self.size
        )  # terrain geometry

    def addMarker(self, origin: Vec3, plotter: QtInteractor) -> Marker:
        """Adds a new marker to the scene and world.

        Args:
            origin (Vec3): Position of marker.
            plotter (QtInteractor): Plotter of main window.

        Returns:
            Marker: The newly added marker.
        """
        marker = Marker(origin)
        marker.setColor([1.0, 1.0, 0.0])
        self.markers.append(marker)
        plotter.add_actor(marker.geom)
        return marker

    def clearMarkers(self, plotter: QtInteractor):
        """Removes all markers from the scene and the world.

        Args:
            plotter (QtInteractor): Plotter of the main window.
        """
        # remove geometries from plotter
        for marker in self.markers:
            plotter.remove_actor(marker.geom)

        # reset markers
        self.markers = []
