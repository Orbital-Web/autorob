from robots.urdf_loader import FromURDF

robot = FromURDF("robots/baxter/baxter.urdf")
robot.selected = robot.joints[5]  # right_s0
robot.endeffector = robot.links[10]  # right_wrist
