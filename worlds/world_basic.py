from kineval import World, Obstacle

obstacles = [
    Obstacle([0.0, -3.0, 0.5], 1.0),
    Obstacle([3.0, 0.0, 0.5], 1.0),
    Obstacle([-3.0, 0.0, 0.5], 1.0),
]

world = World(name="basic", obstacles=obstacles, size=[25, 25])
