import logging
import time
from threading import Thread

from paho.mqtt import client as mqtt_client
from paho.mqtt.client import MQTT_ERR_SUCCESS

# Parameters concerning reconnection behaviour
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


class UR3Robot(object):

    def __init__(self, broker, port, cmd_topic="ur3/set/cmd"):

        # Hostname of broker (e.g. "urpi.local")
        self.broker = broker
        # Port of broker (default: 1883)
        self.port = port

        # Credentials if needed
        # self.username = ''
        # self.password = ''

        # Topic where commands are published
        self.cmd_topic = cmd_topic
        # Global variable to store latest position vector of robot (x,y,z,ax,ay,az)
        self.last_pose = None
        # Global variable to store latest joints vector of robot (j1,j2,j3,j4,j5,j6)
        self.last_joints = None

        self.freedrive = False

        # MQTT client to subscribe and publish to
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)

        self._messages = list()

        self.debug_timing = False
        self.msg_counter = 0
        self.published_messages = dict()
        self.received_returns = dict()

        def on_connect(client, userdata, flags, rc, properties):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        def on_disconnect(client, userdata, rc):
            logging.info("Disconnected with result code: %s", rc)
            reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
            while reconnect_count < MAX_RECONNECT_COUNT:
                logging.info("Reconnecting in %d seconds...", reconnect_delay)
                time.sleep(reconnect_delay)

                try:
                    client.reconnect()
                    logging.info("Reconnected successfully!")
                    return
                except Exception as err:
                    logging.error("%s. Reconnect failed. Retrying...", err)

                reconnect_delay *= RECONNECT_RATE
                reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
                reconnect_count += 1
            logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

        # client.username_pw_set(self.username, self.password)
        self.client.on_connect = on_connect
        self.client.connect(self.broker, self.port)
        self.client.on_disconnect = on_disconnect

        # Subscribe to the val topic to get return values
        self.subscribe("ur3/get/val")

        self.subscriber_thread = Thread(target=self._handle_incoming_val)
        self.subscriber_thread.start()

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.subscriber_thread.join(2)
        self.client.loop_stop()

    def publish(self, msg: str, topic: str):
        """
        Publish message on given topic to MQTT broker
        """
        if self.debug_timing:
            if "movejPose" in msg:
                mid = self.msg_counter
                self.msg_counter += 1
                if self.published_messages.get(topic, None) is None:
                    self.published_messages[topic] = dict()

                if self.published_messages[topic].get(mid, None):
                    raise Exception("Doubled message ID!")

                self.published_messages[topic][mid] = (msg, time.time())

        result = self.client.publish(topic, msg)

        if result.rc is not MQTT_ERR_SUCCESS:
            raise Exception(f"No success publishing message! RC: {result.rc}")


    def subscribe(self, topic):
        """
        Subscribe to given topic on MQTT broker
        """
        self.client.subscribe(topic)

        def on_message(client, userdata, msg):
            """
            Callback function if client receives a message from MQTT broker
            Function where returned position data can be handled
            """
            self._messages.append((client, userdata, msg))

        self.client.on_message = on_message


    def _handle_incoming_val(self):
        while True:
            if self._messages:
                client, userdata, msg = self._messages.pop(0)

                # Decode payload from received message
                decoded_payload = msg.payload.decode()

                # "Type check"
                if "mid" in decoded_payload:
                    mid = int(decoded_payload.split(":")[1])
                    print(f"MID:{mid}")
                    if self.debug_timing:
                        self.received_returns[mid] = (msg, time.time())
                elif "joints" in decoded_payload:
                    # Extract float values from joints string
                    # (e.g. from [0.1, -0.2, 0.1, 1.2, -1.3, 1.1] to x=0.1 y=-0.2, ...)
                    j1, j2, j3, j4, j5, j6 = [float(b) for b in decoded_payload.split(":")[1][2:-1].split(", ")]
                    print(f"Received joints: j1={j1}, j2={j2}, j3={j3}, j4={j4}, j5={j5}, j6={j6}")
                    self.last_joints = [j1, j2, j3, j4, j5, j6]
                elif "pose" in decoded_payload:
                    # Extract float values from pose string
                    # (e.g. from p[0.1, -0.2, 0.1, 1.2, -1.3, 1.1] to x=0.1 y=-0.2, ...)
                    x, y, z, ax, ay, az = [float(b) for b in
                                           decoded_payload.split(":")[1].split("[")[1].split("]")[0].split(", ")]
                    print(f"Received position: x={x}, y={y}, z={z}, ax={ax}, ay={ay}, az={az}")
                    self.last_position = [x, y, z, ax, ay, az]
                elif "force" in decoded_payload:
                    # Extract float values from pose string
                    # (e.g. from p[0.1, -0.2, 0.1, 1.2, -1.3, 1.1] to x=0.1 y=-0.2, ...)
                    fx, fy, fz, tr_x, tr_y, tr_z = [float(b) for b in
                                                    decoded_payload.split(":")[1].split("[")[1].split("]")[0].split(", ")]
                    print(f"Received forces: Fx={fx}, Fy={fy}, Fz={fz}, TRx={tr_x}, TRy={tr_y}, TRz={tr_z}")
                    # self.last_force = [x, y, z, ax, ay, az]
                else:
                    print(f"??? Received {msg.payload.decode()}")

    def move_pos(self, pos):
        """
        Move robo arm to pre-programmed position
        """
        self.publish(f"movePos:{pos}", self.cmd_topic)

    def get_pose(self):
        """
        Get position vector of robo arm
        """
        self.publish(f"getPose:", self.cmd_topic)

    def get_joints(self):
        """
        Get joint positions of robo arm
        """
        self.publish(f"getJoints:", self.cmd_topic)

    def get_forces(self):
        """
        Get forces of robo arm
        """
        self.publish(f"getForces:", self.cmd_topic)

    def start_freedrive(self):
        """
        Start freedrive
        """
        self.freedrive = True
        self.publish(f"free:start", self.cmd_topic)

    def stop_freedrive(self):
        """
        End freedrive
        """
        self.publish(f"free:end", self.cmd_topic)
        self.freedrive = False

    def move_j_pose(self, pose, velocity=None, acceleration=None, blend_radius=None, jtime=None, mid=None):
        """
        Move robo arm to given position (Pose)
        """
        if self.freedrive:
            raise Exception("Can't movej while freedrive mode is active.")

        # Send velocity and acceleration
        if velocity:
            self.publish(f"vel:{velocity}", self.cmd_topic)
        if acceleration:
            self.publish(f"acc:{acceleration}", self.cmd_topic)

        # Send position
        self.publish(f"pose:{pose[0]},{pose[1]},{pose[2]},{pose[3]},{pose[4]},{pose[5]}", self.cmd_topic)

        # If move should be blended into the next one, send blend radius
        if blend_radius:
            self.publish(f"blend:{blend_radius}", self.cmd_topic)

        # If move should take a certain time, send time
        if jtime:
            self.publish(f"time:{jtime}", self.cmd_topic)

        if mid:
            self.publish(f"mid:{mid}", self.cmd_topic)

        self.publish(
            f"movejPose:{'blend' if blend_radius else ''}{',' if blend_radius and jtime else ''}{'time' if jtime else ''}",
            self.cmd_topic)

    def move_j_joints(self, joints, velocity=1.0, acceleration=1.0, blend_radius=None, jtime=None):
        """
        Move robo arm to given position (Joints)
        """
        if self.freedrive:
            raise Exception("Can't movej while freedrive mode is active.")

        # Send velocity and acceleration
        if velocity:
            self.publish(f"vel:{velocity}", self.cmd_topic)
        if acceleration:
            self.publish(f"acc:{acceleration}", self.cmd_topic)

        # Send joints
        self.publish(f"joints:{joints[0]},{joints[1]},{joints[2]},{joints[3]},{joints[4]},{joints[5]}", self.cmd_topic)

        # If move should be blended into the next one, send blend radius
        if blend_radius:
            self.publish(f"blend:{blend_radius}", self.cmd_topic)

        # If move should take a certain time, send time
        if jtime:
            self.publish(f"time:{jtime}", self.cmd_topic)

        self.publish(
            f"movejJoints:{'blend' if blend_radius else ''}{',' if blend_radius and jtime else ''}{'time' if jtime else ''}",
            self.cmd_topic)

    def reduce_speed(self):
        """
        Reduces every movement of the robot to 10 %
        """
        self.publish(f"pause:", self.cmd_topic)

    def reset_speed(self):
        """
        Resets the movement speed after reducing it
        """
        self.publish(f"continue:", self.cmd_topic)

    def evaluate_timing(self):
        """

        NOTES: - send message id with movej cmd and return a message id when it reaches the script
                    then add it to the received returns here

        """
        if not self.debug_timing:
            print("Timing debug is disabled. Set UR3Robot.debug_timing to True.")
        else:
            print("Timing evaluation")
            print("-----------------")
            timings = list()
            for topic in self.published_messages:
                print(f"Topic: {topic}")
                print(f"Published messages: {len(self.published_messages[topic])}")
                if len(self.received_returns) <= 0:
                    print(f"Received returns: 0")
                    print("No timings, since no messages were received.")
                else:
                    print(f"Received returns: {len(self.received_returns)}")
                    print(f"Lost returns: {len(self.published_messages[topic]) - len(self.received_returns)}")
                    for mid in self.published_messages[topic]:
                        message, timing = self.published_messages[topic][mid]
                        r_message, r_timing = self.received_returns.get(mid, (None, None))
                        if r_message is not None:
                            elapsed_time = r_timing - timing
                            timings.append(elapsed_time)
                    print(f"Average elapsed time: {round((sum(timings) / len(timings)) * 1000, 1)} ms")
                    print(f"Max elapsed time: {round((max(timings)) * 1000, 1)} ms")
                    print(f"Min elapsed time: {round((min(timings)) * 1000, 1)} ms")
                    print()
