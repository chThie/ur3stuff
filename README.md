# ur3stuff

## Get started

To run the code of this project you need to install the Eclipse paho mqtt client.  
The required package is listed in a requirements file.

Install required packets via virtual environment (recommended):

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

OR install the packets to your user account:
```
pip install -r requirements.txt
```

## Documentation

For examples how to use the script also see [publisher.py](https://github.com/chThie/ur3stuff/blob/main/publisher.py)
and [subscriber.py](https://github.com/chThie/ur3stuff/blob/main/subscriber.py).

### Usage

#### Connect to robot

```
# Set host and port of mqtt broker
broker = 'localhost'
port = 1883

# Create new client
robot = UR3Robot(broker, port)

# Start client thread for network traffic ("start sending commands and receiving data")
robot.start()

# ...work with the robot

# Stop client thread for network traffic before closing the program
robot.stop()
```

#### Listen for messages

```
# Subscribe to a topic
topic = "ur3/return"
robot.subscribe(topic)

# Now it will listen for messages on this topic...
```

#### Call for position, joints or forces

```
# Call for pose
robot.get_pose()

# Call for joints
robot.get_joints()

# Call for forces
robot.get_forces()
```

#### Moving the robot

```
# Move robo to a given pose with a given blending radius, velocity and acceleration
robot.move_j_pose([0.21, -0.18, 0.50, 1.57, 0.13, 0.01], blend_radius=0.03, velocity=0.5, acceleration=0.2)

# Move robo joints with a given blending radius, velocity and acceleration
robot.move_j_joints([0.2, -0.2, 0.1, 0.50, 1, 1], blend_radius=0.03, velocity=0.5, acceleration=0.2)
```

The movej commands are blocking, since they are designed to queue themselves behind currently running commands.  
This will probably change depending on the needs of our application.

#### Slowing down the robot

```
# Reduces every movement of the robot to 10 %
robot.reduce_speed()

# Resets speed after reducing it
robot.reset_speed()
```

#### Freedrive mode

```
# Start freedrive mode
robot.start_freedrive()

# Stop freedrive mode
robot.stop_freedrive()
```

While freedrive mode is active, the movej commands won't work and raise an exception.
