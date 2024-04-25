import logging
import math
import random
import time

from paho.mqtt import client as mqtt_client

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60


class ur3client(object):

    def __init__(self, broker, port, topic):

        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        # username = 'emqx'
        # password = 'public'

        self.client = client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)

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

        # client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        client.on_disconnect = on_disconnect

    def publish(self, msg):
        result = self.client.publish(self.topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{self.topic}`")
        else:
            print(f"Failed to send message to topic {self.topic}")

    def subscribe(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        self.client.subscribe(self.topic)
        self.client.on_message = on_message

    def move_pos(self, pos):
        self.publish(f"movePos:{pos}")

    def move_j(self, position, orientation, blend_radius=None, velocity=1.0, acceleration=1.0):
        self.publish(f"vel:{velocity}")
        self.publish(f"acc:{acceleration}")

        self.publish(f"x:{position[0]}")
        self.publish(f"y:{position[1]}")
        self.publish(f"z:{position[2]}")
        self.publish(f"ax:{orientation[0]}")
        self.publish(f"ay:{orientation[1]}")
        self.publish(f"az:{orientation[2]}")

        # send
        if blend_radius:
            self.publish(f"blend:{blend_radius}")
            self.publish(f"movej:blend")
        else:
            self.publish(f"movej:")

    def pause(self):
        self.publish(f"pause:")

    def continue_after_pause(self):
        self.publish(f"continue:")


def run():
    broker = 'localhost'
    #broker = 'urpi.local'
    port = 1883
    topic = "ur3/set/cmd"

    our_client = ur3client(broker, port, topic)
    our_client.client.loop_start()

    # our_client.move_pos(7)

    our_client.move_j(position=[10.0, 20.0, 30.0], orientation=[-10.0, -20.0, 10.0],
                      blend_radius=0.1,
                      velocity=math.radians(180) / 2,
                      acceleration=math.radians(180) / 4)

    # our_client.move_j([10.0, 20.0, 30.0], [-10.0, -20.0, 10.0], math.radians(180) / 2, math.radians(180) / 4)
    # our_client.pause()
    # our_client.continue_after_pause()

    our_client.client.loop_stop()


if __name__ == '__main__':
    run()
