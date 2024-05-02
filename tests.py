import math
import time


def test_upright(robot):
    upright_j1 = math.radians(0)
    upright_j2 = math.radians(-90)
    upright_j3 = math.radians(0)
    upright_j4 = math.radians(-90)
    upright_j5 = math.radians(-180)
    upright_j6 = math.radians(0)

    # Test which should move the robo upright
    robot.move_j_joints([upright_j1, upright_j2, upright_j3, upright_j4, upright_j5, upright_j6])
    time.sleep(3)

    # Test to turn the first axis
    robot.move_j_pose([math.radians(180), upright_j2, upright_j3, upright_j4, upright_j5, upright_j6])
    time.sleep(3)

    # Test to turn the second axis
    robot.move_j_pose([math.radians(180), math.radians(-180), upright_j3, upright_j4, upright_j5, upright_j6])
    time.sleep(3)
    robot.move_j_pose([math.radians(180), math.radians(0), upright_j3, upright_j4, upright_j5, upright_j6])
    time.sleep(3)

    # Test to turn the tool tip
    robot.move_j_pose([math.radians(180), math.radians(0), upright_j3, upright_j4, upright_j5, math.radians(180)])
    time.sleep(3)
    robot.move_j_pose([math.radians(180), math.radians(0), upright_j3, upright_j4, upright_j5, math.radians(0)])


def test_box(robot):
    # Test to move robo to a given position in the given time (seconds)
    robot.move_j_pose([0.21, -0.18, 0.50, 1.57, 0.3, 0.01], velocity=0.5, acceleration=0.2)
    time.sleep(5)

    # Test1
    pose1 = [-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose1)
    time.sleep(3)

    pose4 = [-0.299747, 0.1656, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose4)
    time.sleep(3)

    # Test2

    pose1 = [-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose1)
    time.sleep(3)

    pose2 = [-0.299747, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose2)
    time.sleep(3)

    pose3 = [-0.299747, 0.1656, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose3)
    time.sleep(3)

    pose4 = [-0.195975, 0.1656, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose4)
    time.sleep(3)

    pose5 = [-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose5)
    time.sleep(3)

    pose1 = [-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose1)
    time.sleep(3)

    pose2 = [-0.299747, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose2)
    time.sleep(3)

    pose3 = [-0.299747, 0.1656, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose3)
    time.sleep(3)

    pose4 = [-0.195975, 0.1656, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose4)
    time.sleep(3)

    pose5 = [-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose5)
