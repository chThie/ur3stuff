from ur3robot import UR3Robot

from tests import *


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
    # robot.move_j_pose([0.21, -0.18, 0.50, 1.57, 0.13, 0.01], blend_radius=0.03, velocity=0.5, acceleration=0.2)

    # run test function
    test_line(robot)

    # END of programming movements
    # ------------------------------

    # our_client.pause()
    # our_client.continue_after_pause()

    # Stop client thread for network traffic before closing the program
    robot.stop()


if __name__ == '__main__':
    run()
