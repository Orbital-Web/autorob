from kineval import World, Obstacle
import numpy as np

obstacles = []
for i in range(100):
    # create obstacles whilst ensuring the don't spawn in the center
    rand_dir = np.where(np.random.rand(2) > 0.5, 1, -1)
    rand_r = np.random.rand() * 3 + 0.5
    rand_xy = rand_dir * (np.random.rand(2) * (24 - rand_r) + rand_r + 1)
    rand_z = np.random.rand() * 3 - 0.6
    obstacles.append(Obstacle([*rand_xy, rand_z], rand_r))

world = World(name="random", obstacles=obstacles, size=[50, 50])
