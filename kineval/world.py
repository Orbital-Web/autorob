from kineval import Vec2
import numpy as np
import pyvista as pv


class World:
    """A class for holding all the obstacles, terrain,
    etc. that are in the world."""

    def __init__(self):
        self.obstacles: list = []  # list of obstacles
        self.terrain: pv.Actor = None  # terrain geometry
        self.bounds: Vec2 = np.array([10.0, 10.0], float)  # x and y bounds of the world
