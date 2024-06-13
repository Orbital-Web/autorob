from kineval import Vec2
from robots import Plane
import numpy as np
import pyvista as pv


class World:
    """A class for holding all the obstacles, terrain,
    etc. that are in the world."""

    def __init__(self, name: str, obstacles: list = None, bounds: Vec2 = None):
        self.name: str = name  # name of world
        self.obstacles: list = (
            [] if obstacles is None else obstacles
        )  # list of obstacles
        self.bounds: Vec2 = (
            np.array([10.0, 10.0], float) if bounds is None else np.array(bounds, float)
        )  # x and y bounds of the world
        self.terrain: pv.Actor = Plane(
            origin=[0.0, 0.0, -0.01], normal=[0.0, 0.0, 1.0], size=self.bounds
        )  # terrain geometry
