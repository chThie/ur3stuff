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

    # Subscribe to a topic
    topic = "ur3/get/val"
    robot.subscribe(topic)

    # Now it will listen for messages on this topic...

    print("Starting to listen to {topic}:")
    input("Press any key to stop...")

    # Stop client thread for network traffic before closing the program
    robot.stop()


if __name__ == '__main__':
    run()
