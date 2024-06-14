from robots.urdf_loader import FromURDF

robot = FromURDF("robots/fetch/fetch.urdf")
robot.endeffector = robot.links[14]  # r_gripper_finger_link
