import logging
import math
import time

from paho.mqtt import client as mqtt_client

# Parameters concerning reconnection behaviour
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


class ur3client(object):

    def __init__(self, broker, port, cmd_topic="ur3/set/cmd"):

        # Hostname of broker (e.g. "urpi.local")
        self.broker = broker
        # Port of broker (default: 1883)
        self.port = port

        # Credentials if needed
        # self.username = 'emqx'
        # self.password = 'public'

        # Topic where commands are published
        self.cmd_topic = cmd_topic
        # Global variable to store latest position vector of robot (x,y,z,ax,ay,az)
        self.last_position = None

        # MQTT client to subscribe and publish to
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)

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

    def publish(self, msg: str, topic: str):
        """
        Publish message on given topic to MQTT broker
        """
        result = self.client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

    def subscribe(self, topic):
        """
        Subscribe to given topic on MQTT broker
        """

        def on_message(client, userdata, msg):
            """
            Callback function if client receives a message from MQTT broker
            Function where returned position data can be handled
            """
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            if topic == "ur3/get/joints":
                # Decode payload from received message
                decoded_payload = msg.payload.decode()
                # Extract float values from pose string
                # (e.g. from p[0.1, -0.2, 0.1, 1.2, -1.3, 1.1] to x=0.1 y=-0.2, ...)
                x, y, z, ax, ay, az = [float(x) for x in decoded_payload.split("[")[1].split("]")[0].split(", ")]
                self.last_position = [x, y, z, ax, ay, az]
                print(f"Received position: x={x}, y={y}, z={z}, ax={ax}, ay={ay}, az={az}")

        self.client.subscribe(topic)
        self.client.on_message = on_message

    def move_pos(self, pos):
        """
        Move robo arm to pre-programmed position
        """
        self.publish(f"movePos:{pos}", self.cmd_topic)

    def move_j(self, position, orientation, blend_radius=None, velocity=1.0, acceleration=1.0):
        """
        Move robo arm to given position
        """
        # Send velocity and acceleration
        self.publish(f"vel:{velocity}", self.cmd_topic)
        self.publish(f"acc:{acceleration}", self.cmd_topic)

        # Send position
        self.publish(f"x:{position[0]}", self.cmd_topic)
        self.publish(f"y:{position[1]}", self.cmd_topic)
        self.publish(f"z:{position[2]}", self.cmd_topic)

        # Send orientation
        self.publish(f"ax:{orientation[0]}", self.cmd_topic)
        self.publish(f"ay:{orientation[1]}", self.cmd_topic)
        self.publish(f"az:{orientation[2]}", self.cmd_topic)

        # If move should be blended into the next one, send blend radius
        if blend_radius:
            self.publish(f"blend:{blend_radius}", self.cmd_topic)
            self.publish(f"movej:blend", self.cmd_topic)
        else:
            self.publish(f"movej:", self.cmd_topic)

    # untested
    def pause(self):
        self.publish(f"pause:", self.cmd_topic)

    # untested
    def continue_after_pause(self):
        self.publish(f"continue:", self.cmd_topic)


def run():
    # Set host and port of mqtt broker

    # broker = 'localhost'
    broker = 'urpi.local'
    port = 1883

    # Create new client
    our_client = ur3client(broker, port)

    # Start client thread for network traffic ("start sending commands and receiving data")
    our_client.client.loop_start()

    # Subscribe to joints topic to receive updates on position of robo arm
    our_client.subscribe("ur3/get/joints")

    # ------------------------------
    # BEGIN of programming movements

    # Test to move robo to pre-programmed position with no. 3
    our_client.move_pos(3)

    # Test to move robo to a given position with a given orientation, blending, velocity and acceleration
    our_client.move_j(position=[0.1, 0.1, 0.1], orientation=[math.radians(70), math.radians(50), math.radians(-70)],
                      blend_radius=0.03,
                      velocity=math.radians(180) / 2,
                      acceleration=math.radians(180) / 4)

    # Test to move robo to another position without changing velocity etc.
    our_client.move_j([0.12, 0.12, 0.12], [math.radians(65), math.radians(55), math.radians(-65)])

    # END of programming movements
    # ------------------------------

    # our_client.pause()
    # our_client.continue_after_pause()

    # Stop client thread for network traffic before closing the program
    our_client.client.loop_stop()


if __name__ == '__main__':
    run()
