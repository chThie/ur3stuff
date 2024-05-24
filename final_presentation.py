import multiprocessing
import sys

from ur3robot import UR3Robot
from ur3interpreter import UR3Interpreter

import random
import time
import leap

from leap import datatypes as ldt
import requests

from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from multiprocessing import Process

# Mode selection: "COUNT" or "GEST"
MODE_SELECTION = "GEST"

# How often the tracking should occur
TRACKING_INTERVAL_FRAMES = 5

# Number of pumps required for gesture recognition
GESTURE_PUMP_THRESHOLD = 3

# Threshold for detecting significant palm position change
PALM_POSITION_THRESHOLD = 20.0

# Constants defining states for tracking the z-axis movement
UP = 0
DOWN = 1
STOP = 2

# Mapping from digit index to finger name
DIGIT_TO_FINGER = {
    0: "Thumb",
    1: "Index",
    2: "Middle",
    3: "Ring",
    4: "Pinky"
}

# Computer gestures
COMPUTER_GESTURES = ['Rock', 'Paper', 'Scissors']

# Outcomes dictionary
OUTCOMES = {
    'Rock': {'Rock': 'It\'s a tie', 'Paper': 'Computer wins', 'Scissors': 'You win!'},
    'Paper': {'Rock': 'You win!', 'Paper': 'It\'s a tie', 'Scissors': 'Computer wins'},
    'Scissors': {'Rock': 'Computer wins', 'Paper': 'You win!', 'Scissors': 'It\'s a tie'}
}

CURRENT_ARDUINO_GESTURE = ""

TIME_BETWEEN_SENDING_MOVES = 0.5
TIME_ROBOT_HAS_FOR_ONE_MOVE = 0.3

POSITION = multiprocessing.Array("f",[-0.120587, -0.393911, 0.3, 0.232045, 2.11675, -2.084526])



# Function to get the location at the end of a finger
def get_end_of_finger_location(hand: ldt.Hand, digit_index: int) -> ldt.Vector:
    digit = hand.digits[digit_index]
    return digit.distal.next_joint


# Function to recognize hand gesture
def recognize_hand_gesture(hand: ldt.Hand) -> str:
    extended_fingers = {DIGIT_TO_FINGER[digit_index] for digit_index in range(5) if
                        hand.digits[digit_index].is_extended}

    if not extended_fingers or set(extended_fingers) == {"Thumb"}:
        return "Rock"
    elif set(extended_fingers) == {"Index", "Middle"} or set(extended_fingers) == {"Thumb", "Index", "Middle"} or set(
            extended_fingers) == {"Thumb", "Index", "Middle", "Ring"} or set(extended_fingers) == {"Index", "Middle",
                                                                                                   "Ring"}:
        return "Scissors"
    elif set(extended_fingers) == {"Thumb", "Index", "Middle", "Ring", "Pinky"} or set(extended_fingers) == {"Index",
                                                                                                             "Middle",
                                                                                                             "Ring",
                                                                                                             "Pinky"} or set(
        extended_fingers) == {"Index", "Middle", "Pinky"} or set(extended_fingers) == {"Thumb", "Index", "Middle",
                                                                                       "Pinky"}:
        return "Paper"
    else:
        return "Unknown"


# Function to send signal to specific URL based on computer gesture
def send_signal(computer_gesture):
    global CURRENT_ARDUINO_GESTURE
    if computer_gesture == CURRENT_ARDUINO_GESTURE:
        # print(f"Hand already set to {computer_gesture}")
        return
    url = f"http://192.168.0.128/signal/{computer_gesture.lower()}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Successfully sent signal for {computer_gesture}")
            CURRENT_ARDUINO_GESTURE = computer_gesture
        else:
            print(f"Failed to send signal for {computer_gesture}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending signal for {computer_gesture}: {e}")


class HandGestureListener(leap.Listener):

    def calculate_and_set_position(self, hand_pos):
        hand_max_z = 500
        player_max_z = 500
        adjusted_z = hand_pos
        if hand_pos > player_max_z:
            adjusted_z = player_max_z
        z_min = 0.2
        z_max = 0.5
        z_val = z_min + (adjusted_z / hand_max_z) * (z_max - z_min)

        hand_angle_min_a = 0.35
        hand_angle_max_a = 0.1
        hand_angle_val_a = hand_angle_min_a + ((hand_pos) / hand_max_z) * (
                hand_angle_max_a - hand_angle_min_a)

        hand_angle_min_b = 2.4
        hand_angle_max_b = 1.3
        hand_angle_val_b = hand_angle_min_b + ((hand_pos) / hand_max_z) * (
                hand_angle_max_b - hand_angle_min_b)

        hand_angle_min_c = -1.6
        hand_angle_max_c = -2.6
        hand_angle_val_c = hand_angle_min_c + ((hand_pos) / hand_max_z) * (
                hand_angle_max_c - hand_angle_min_c)
        pos_tuple = (-0.120587, -0.393911, z_val, hand_angle_val_a, hand_angle_val_b, hand_angle_val_c)

        for index, entry in enumerate(pos_tuple):
            self.global_position[index] = entry

    def __init__(self, output_text, result_text, pumps, global_position):
        super().__init__()
        self.global_position = global_position

        self.output_text = output_text
        self.result_text = result_text
        self.pumps = pumps
        self.is_first_frame = True
        self.reset()
        self.error_triggered = None
        self.up_hit = False
        self.COMPUTER_WINS = 0
        self.PLAYER_WINS = 0
        self.output_text("Waiting")
        send_signal("Rock")

        # Reset listener state

    def reset(self):
        self.pump_count = 0
        self.z_axis_state = None
        self.counted = False
        self.error_triggered = True
        self.previous_palm_position = 0
        self.should_recognize_gesture = False
        self.is_first_frame = True
        self.up_hit = False
        send_signal("Rock")

    def soft_reset(self):
        self.pump_count = 0
        self.counted = False
        self.error_triggered = False
        self.should_recognize_gesture = False
        self.z_axis_state = None
        self.up_hit = False

        # On Leap Motion controller connection

    def on_connect(self, controller):
        self.reset()

    def on_tracking_event(self, event):
        #print("tracking")
        if event.tracking_frame_id % TRACKING_INTERVAL_FRAMES != 0:
            return

        if not event.hands:
            if not self.is_first_frame and not self.should_recognize_gesture:
                self.reset()
                self.error_triggered = True
                self.output_text("No hands in frame")
            return

        if len(event.hands) > 1:
            self.reset()
            self.output_text("More than 1 hand in frame")
            self.error_triggered = True
            return

        hand = event.hands[0]
        palm_position = hand.palm.position.y

        self.calculate_and_set_position(palm_position)

        if not self.is_first_frame and not self.should_recognize_gesture:
            position_difference = palm_position - self.previous_palm_position
            if abs(position_difference) > PALM_POSITION_THRESHOLD:
                if position_difference > 0:
                    self.z_axis_state = UP
                    self.up_hit = True
                elif position_difference < 0:
                    self.z_axis_state = DOWN
                    self.counted = False
            else:
                if self.z_axis_state == DOWN and not self.counted and self.up_hit:
                    self.pump_count += 1
                    self.output_text(f"{self.pump_count}")
                    self.counted = True
                    self.up_hit = False
                elif self.z_axis_state == UP and self.pump_count == 0:  # The first upswing
                    self.output_text(f"Ready")
                    self.z_axis_state = STOP
                    send_signal("Rock")

            if self.z_axis_state == DOWN and self.pump_count >= GESTURE_PUMP_THRESHOLD:
                self.should_recognize_gesture = True
        else:
            self.output_text(f"Hand detected")
            self.error_triggered = False
            self.is_first_frame = False

        self.previous_palm_position = palm_position

        if self.should_recognize_gesture:
            player_gesture = recognize_hand_gesture(hand)
            if player_gesture != "Unknown":
                if random.randint(1, 8) == 1:
                    computer_gesture = self.winning_move(player_gesture)
                else:
                    computer_gesture = random.choice(COMPUTER_GESTURES)
                winner = OUTCOMES[player_gesture][computer_gesture]
                self.output_text(f"You: {player_gesture}\nComputer: {computer_gesture}\n{winner}")
                self.update_scores(winner)
                send_signal(computer_gesture)  # Send signal based on computer gesture
                time.sleep(1)
                self.soft_reset()

    def update_scores(self, winner):
        if winner == "You win!":
            self.PLAYER_WINS += 1
        elif winner == "Computer wins":
            self.COMPUTER_WINS += 1
        self.result_text(f"Computer {self.COMPUTER_WINS} - {self.PLAYER_WINS} Player")

    def winning_move(self, move):
        if move == "Rock":
            return "Paper"
        if move == "Scissors":
            return "Rock"
        if move == "Paper":
            return "Scissors"


class HandGestureWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rock Paper Scissors")
        self.setStyleSheet("background-color: black; color: white; font-size: 48px; font-weight: bold;")
        self.output_label = QLabel()
        self.result_label = QLabel()

        layout = QVBoxLayout()
        layout.addWidget(self.output_label)
        layout.addWidget(self.result_label)
        self.setLayout(layout)
        self.setGeometry(100, 100, 1000, 800)
        self.pumps = [None, None, None, None]  # Define pumps as needed

    def update_output_text(self, text):
        self.output_label.setText(text)

    def update_result_text(self, text):
        self.result_label.setText(text)


def run_leap(global_position):
    app = QApplication(sys.argv)
    window = HandGestureWindow()
    window.show()

    listener = HandGestureListener(window.update_output_text, window.update_result_text, window.pumps, global_position)
    connection = leap.Connection()
    connection.add_listener(listener)

    with connection.open():
        sys.exit(app.exec_())


# Main function
def main():
    broker = 'urpi.local'
    port = 1883

    robot = UR3Robot(broker, port)

    robot.start()
    robot.publish("interpret", "ur3/set/cmd")
    time.sleep(0.5)

    interpreter = UR3Interpreter()
    interpreter.time_for_each_movej = TIME_ROBOT_HAS_FOR_ONE_MOVE
    time.sleep(0.5)

    interpreter.time_for_each_movej = TIME_ROBOT_HAS_FOR_ONE_MOVE

    interpreter.movejJoints(-1.627241, -1.78029, -1.245485, -3.267259, -1.727941, -2.780924)


    interpreter.movejPose(tuple(POSITION))

    leap_process = Process(target=run_leap, args=(POSITION,))  # Changed to use multiprocessing.Process

    leap_process.start()

    while True:
        print("Main: ",tuple(POSITION))
        interpreter.movejPose(tuple(POSITION))
        time.sleep(TIME_BETWEEN_SENDING_MOVES)


if __name__ == "__main__":
    main()
