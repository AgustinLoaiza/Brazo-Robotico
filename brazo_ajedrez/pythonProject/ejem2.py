#Code for Chess Robot Inverse Kinematics

import math
import serial
from time import sleep

SQUARE_SIZE = 3.5
offset = 6

filemap = {
    "h": 3.5+0.2, "g": 2.5+0.1, "f": 1.5, "e": 0.5-0.2,
    "d": -0.5-0.3, "c": -1.5, "b": -2.5, "a": -3.5
}

class ChessRobotArm:
    def __init__(self, a: int, b: int, port='COM11', verbose=False) -> None:
        self.port = port
        self.ser = serial.Serial(port)
        print(f"Connected to Robot on port {port}")

        self.a = a
        self.b = b
        self.verbose = verbose

    def wait_until_msg(self, msg: str) -> None:
        while True:
            rec = self.ser.readline().decode().strip()
            if msg in rec:
                break

    def command(self, num: int, wait=True) -> None:
        self.ser.write(bytes(str(num), 'utf-8'))
        sleep(0.05)
        if wait:
            self.wait_until_msg("done")

    def combo_move(self, sangle, eangle):
        self.command(eangle + 200)
        self.command(sangle)

    def base_to(self, angle: int) -> None:
        self.command(angle + 400)

    def rest(self) -> None:
        self.command(190)

    def grasp(self) -> None:
        self.command(191)

    def drop(self) -> None:
        self.command(192)

    def base_angle(self, x: float, y: float):
        y += offset/SQUARE_SIZE + 0.3
        d = math.sqrt((x*SQUARE_SIZE)**2 + (y*SQUARE_SIZE)**2)
        angle = math.atan(y/x)*180/math.pi
        if angle < 0:
            angle += 180
        if x < 0:
            angle -= x*3
        return d, angle

    def inverse_kinematics(self, x: float, y: float):
        elbow_theta = math.acos(
            (x**2 + y**2 - self.a**2 - self.b**2) / (2*self.a*self.b)
        )
        shoulder_theta = math.atan(y/x) - math.atan(
            (self.b*math.sin(elbow_theta)) /
            (self.a + self.b*math.cos(elbow_theta))
        )
        return (-shoulder_theta*180/math.pi, 180 - elbow_theta*180/math.pi)

    def go_to(self, square: str):
        x = filemap[square[0]]
        rank = int(square[1])
        y = rank + 0.5

        d, base_ang = self.base_angle(x, y)

        # -------- COMPENSACIÓN POR TABLERO INCLINADO --------
        tilt_cm_per_rank = 8 / 7.0   # ≈ 0.85 cm
        tilt_comp = (rank - 1) * tilt_cm_per_rank

        vertical_offset = -6 + rank/3.5 - tilt_comp
        # ----------------------------------------------------

        s, e = self.inverse_kinematics(vertical_offset, d + rank/10)
        e -= 3

        b_offset = 1
        self.base_to(base_ang + b_offset)
        self.combo_move(s-90, e)

if __name__ == '__main__':
    robot = ChessRobotArm(21, 27, port='COM11', verbose=True)

    while True:
        sq = input("Casilla: ")
        robot.drop()
        robot.go_to(sq)
        robot.grasp()
        robot.rest()
        robot.drop()
