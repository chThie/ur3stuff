from ur3robot import UR3Robot


def run():
    # Set host and port of mqtt broker

    # broker = 'localhost'
    broker = 'urpi.local'
    port = 1883

    # Create new client
    robot = UR3Robot(broker, port)

    # Start client thread for network traffic ("start sending commands and receiving data")
    robot.start()

    # ------------------------------
    # START of programming movements

    # Test to move robo to a given position with a given orientation, blending, velocity and acceleration
    robot.move_j_pose([0.21, -0.18, 0.50, 1.57, 0.13, 0.01], blend_radius=0.03, velocity=0.5, acceleration=0.2)

    # Test1
    pose1 = [-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose1)

    pose4 = [-0.299747, 0.1656, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose4)

    # Test2
    pose1 = [-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose1)

    pose2 = [-0.299747, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose2)

    pose3 = [-0.299747, 0.1656, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose3)

    pose4 = [-0.299747, 0.1656, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose4)

    # Test3

    pose1 = [-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose1)

    pose2 = [-0.299747, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose2)

    pose3 = [-0.299747, 0.1656, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose3)

    pose4 = [-0.195975, 0.1656, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose4)

    pose5 = [-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose5)

    pose1 = [-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose1)

    pose2 = [-0.299747, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose2)

    pose3 = [-0.299747, 0.1656, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose3)

    pose4 = [-0.195975, 0.1656, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose4)

    pose5 = [-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573]
    robot.move_j_pose(pose5)

    # END of programming movements
    # ------------------------------

    # our_client.pause()
    # our_client.continue_after_pause()

    # Stop client thread for network traffic before closing the program
    robot.stop()


if __name__ == '__main__':
    run()
