import socket
import time
from threading import Thread

import numpy as np


class UR3Interpreter:
    def __init__(self):
        server_host = '10.3.3.14'
        server_port = 30020
        self.s = socket.socket()
        self.s.connect((server_host, server_port))
        self.position = None
        self.time_for_each_movej = 0.0

    def movejPose(self, p, a=1.4, v=1.05, r=0.02):
        x, y, z, ax, ay, az = p
        self.send_cmd(f'movej(p[{x},{y},{z},{ax},{ay},{az}], a={a}, v={v}, t={self.time_for_each_movej}, r={r})')

    def movejJoints(self, j1, j2, j3, j4, j5, j6):
        self.send_cmd(f'movej([{j1},{j2},{j3},{j4},{j5},{j6}], a=1.4, v=1.05, t=0.2, r=0)')

    def send_cmd(self, cmd):
        self.s.send(f"{cmd}\n".encode())
        data = self.s.recv(1024)
        print('Received', repr(data))

    def stop(self):
        self.s.close()

    def set_z_position(self, z):
        self.position = (-0.195975, -0.24307, z, -1.460951, -0.986934, 1.547573)

    def generate_positions(self):
        counter = 0
        positions = [(-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.18, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.45, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573),
                     (-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573)]
        while True:
            self.position = positions[counter]
            counter = (counter + 1) % len(positions)
            time.sleep(0.1)


def test_sth():
    positions = [(-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.18, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.45, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573),
                 (-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573)]

    pos_before = None
    for index, position in enumerate(positions):
        if not pos_before:
            pos_before = position
            continue
        dist = distance_3d(pos_before[:3], position[:3])


def test_up_down(robot):
    robot.movejJoints(0.0, -1.5707963267948966, 0.0, -1.5707963267948966, -3.141592653589793, 0.0)

    while True:
        robot.movejPose(robot.position)
        time.sleep(0.2)

    # pos1 = (-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573)
    # pos2 = (-0.195975, -0.24307, 0.18, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos1[:3], pos2[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos1, blend_radius)
    # pos3 = (-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos2[:3], pos3[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos2, blend_radius)
    # pos4 = (-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos3[:3], pos4[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos3, blend_radius)
    # pos5 = (-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos4[:3], pos5[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos4, blend_radius)
    # pos6 = (-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos5[:3], pos6[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos5, blend_radius)
    # pos7 = (-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos6[:3], pos7[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos6, blend_radius)
    # pos8 = (-0.195975, -0.24307, 0.45, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos7[:3], pos8[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos7, blend_radius)
    # pos9 = (-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos8[:3], pos9[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos8, blend_radius)
    # pos10 = (-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos9[:3], pos10[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos9, blend_radius)
    # pos11 = (-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos10[:3], pos11[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos10, blend_radius)
    # pos12 = (-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573)
    # blend_radius = distance_3d(pos11[:3], pos12[:3]) / 2
    # print(blend_radius)
    # robot.movejPose(pos11, blend_radius)


def distance_3d(c1, c2):
    p1 = np.array(c1)
    p2 = np.array(c2)
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    dist = np.sqrt(squared_dist)
    return dist

# for i in range(3):
#     robot.movejPose(-0.195975, -0.24307, 0.150455, -1.460951, -0.986934, 1.547573)
#     print(distance_3d([-0.195975, -0.24307, 0.150455], [-0.195975, -0.24307, 0.18]))
#     robot.movejPose(-0.195975, -0.24307, 0.18, -1.460951, -0.986934, 1.547573)
#     print(distance_3d([-0.195975, -0.24307, 0.18], [-0.195975, -0.24307, 0.23]))
#     robot.movejPose(-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.343826, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.45, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.4, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.3, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.27, -1.460951, -0.986934, 1.547573)
#     robot.movejPose(-0.195975, -0.24307, 0.23, -1.460951, -0.986934, 1.547573)

# robot.movejJoints(0.0, -1.5707963267948966, 0.0, -1.5707963267948966, -3.141592653589793, 0.0)
