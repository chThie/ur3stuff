import time
from threading import Thread

from ur3robot import UR3Robot
from ur3interpreter import UR3Interpreter

import leap

TIME_BETWEEN_SENDING_MOVES = 0.4
TIME_ROBOT_HAS_FOR_ONE_MOVE = 0.2

POSITION = (-0.120587, -0.393911, 0.3, 0.232045, 2.11675, -2.084526)


class LeapThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.listener = HandGestureListener()
        self.connection = leap.Connection()
        self.connection.add_listener(self.listener)


class HandGestureListener(leap.Listener):

    def on_tracking_event(self, event):
        global POSITION
        for hand in event.hands:
            hand_type = "Left" if str(hand.type) == "HandType.Left" else "Right"
            if hand_type == "Left":
                z_min = 0.2
                z_max = 0.6
                z_val = z_min + ((hand.palm.position.y) / 700) * (z_max - z_min)
                hand_angle_min_a = 0.35
                hand_angle_max_a = 0.1
                hand_angle_val_a = hand_angle_min_a + ((hand.palm.position.y) / 700) * (
                            hand_angle_max_a - hand_angle_min_a)

                hand_angle_min_b = 2.4
                hand_angle_max_b = 1.3
                hand_angle_val_b = hand_angle_min_b + ((hand.palm.position.y) / 700) * (
                            hand_angle_max_b - hand_angle_min_b)

                hand_angle_min_c = -1.6
                hand_angle_max_c = -2.6
                hand_angle_val_c = hand_angle_min_c + ((hand.palm.position.y) / 700) * (
                            hand_angle_max_c - hand_angle_min_c)
                POSITION = (-0.120587, -0.393911, z_val, hand_angle_val_a, hand_angle_val_b, hand_angle_val_c)
                print(hand_angle_val_a, hand_angle_val_b, hand_angle_val_c)


broker = 'urpi.local'
port = 1883

# Create new client
robot = UR3Robot(broker, port)

robot.start()
robot.publish("interpret", "ur3/set/cmd")
time.sleep(0.5)

interpreter = UR3Interpreter()
interpreter.time_for_each_movej = TIME_ROBOT_HAS_FOR_ONE_MOVE
time.sleep(0.5)

leap_thread = LeapThread()
leap_thread.start()
time.sleep(0.5)

interpreter.time_for_each_movej = TIME_ROBOT_HAS_FOR_ONE_MOVE

interpreter.movejJoints(0.0, -1.5707963267948966, 0.0, -1.5707963267948966, -3.141592653589793, 0.0)

interpreter.movejPose(POSITION)

try:
    with leap_thread.connection.open():
        while True:
            interpreter.movejPose(POSITION)
            time.sleep(TIME_BETWEEN_SENDING_MOVES)
except KeyboardInterrupt:
    interpreter.send_cmd("end_interpreter()")
    robot.stop()
    leap_thread.join()
