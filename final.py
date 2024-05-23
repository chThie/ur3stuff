import threading
import time
from threading import Thread

from ur3robot import UR3Robot
from ur3interpreter import UR3Interpreter

import leap

TIME_BETWEEN_SENDING_MOVES = 0.1
TIME_ROBOT_HAS_FOR_ONE_MOVE = 0.1

POSITION = None

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
                z_diff = ((hand.palm.position.y - 100) / 600) * 0.5
                POSITION = (-0.195975, -0.24307, 0.150455+z_diff, -1.460951, -0.986934, 1.547573)
                print(z_diff)


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

interpreter.movejJoints(0.0, -1.5707963267948966, 0.0, -1.5707963267948966, -3.141592653589793, 0.0)


# t = Thread(target=interpreter.generate_positions)
# t.start()
POSITION = (-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573)

interpreter.movejPose(POSITION, a=1.0, v=1.0)

try:
    with leap_thread.connection.open():
        while True:
            interpreter.movejPose(POSITION)
            time.sleep(TIME_BETWEEN_SENDING_MOVES)
except KeyboardInterrupt:
    interpreter.send_cmd("end_interpreter()")
    robot.stop()
    leap_thread.join()
    # t.join()
