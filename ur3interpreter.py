import socket
import time


class UR3Interpreter:
    def __init__(self):
        server_host = '10.3.3.14'
        server_port = 30020
        self.s = socket.socket()
        self.s.connect((server_host, server_port))
        self.time_for_each_movej = 0.0

    def movejPose(self, p, a=1.4, v=1.05, r=0.0):
        x, y, z, ax, ay, az = p
        self.send_cmd(f'movej(p[{x},{y},{z},{ax},{ay},{az}], a={a}, v={v}, t={self.time_for_each_movej}, r=0.01)')

    def movejJoints(self, j1, j2, j3, j4, j5, j6):
        self.send_cmd(f'movej([{j1},{j2},{j3},{j4},{j5},{j6}], a=1.4, v=1.05, t=0.2, r=0)')

    def send_cmd(self, cmd):
        self.s.send(f"{cmd}\n".encode())
        data = self.s.recv(1024)
        # print('Received', repr(data))

    def stop(self):
        self.s.close()

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



