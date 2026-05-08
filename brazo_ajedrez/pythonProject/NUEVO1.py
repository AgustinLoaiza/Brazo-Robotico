# Code for Chess Robot Inverse Kinematics (VERSIÓN LIMPIA)

import math
import serial
from time import sleep

SQUARE_SIZE = 4  # cm

class ChessRobotArm:
    def __init__(self, a: int, b: int, port='COM4', verbose=False) -> None:
        self.port = port
        self.ser = serial.Serial(port, 9600)
        print(f"Connected to Robot on port {port}")

        self.a = a  # hombro → codo
        self.b = b  # codo → pinza

        self.verbose = verbose

    # ---------------- COMUNICACIÓN ----------------

    def wait_until_msg(self, msg: str) -> None:
        while True:
            rec = self.ser.readline().decode().strip()
            if msg in rec:
                break
            else:
                print("Received:", rec)

    def command(self, num: int, wait=True) -> None:
        self.ser.write((str(int(num)) + '\n').encode())
        if self.verbose:
            print("Sent:", num)
        sleep(0.05)
        if wait:
            self.wait_until_msg("done")

    # ---------------- MOVIMIENTO ----------------

    def combo_move(self, shoulder, elbow):
        self.command(elbow + 200)
        self.command(shoulder)

    def base_to(self, angle: int):
        self.command(angle + 400)

    def rest(self):
        self.command(190)

    def grasp(self):
        self.command(191)

    def drop(self):
        self.command(192)

    # ---------------- CINEMÁTICA ----------------

    def inverse_kinematics(self, z: float, d: float):
        r = math.sqrt(d**2 + z**2)

        cos_elbow = (r**2 - self.a**2 - self.b**2) / (2*self.a*self.b)

        # evitar errores de dominio
        cos_elbow = max(min(cos_elbow, 1), -1)

        elbow = math.acos(cos_elbow)

        shoulder = math.atan2(z, d) - math.atan2(
            self.b * math.sin(elbow),
            self.a + self.b * math.cos(elbow)
        )

        return (
            int(math.degrees(shoulder)),
            int(180 - math.degrees(elbow))
        )

    # ---------------- TABLERO ----------------

    def square_to_xy(self, square):
        file = square[0]
        rank = int(square[1])

        # centro del tablero = (0,0)
        x = (ord(file) - ord('d') - 0.5) * SQUARE_SIZE
        y = (rank - 4.5) * SQUARE_SIZE

        return x, y

    # ---------------- IR A CASILLA ----------------

    def go_to(self, square: str):
        x, y = self.square_to_xy(square)

        # distancia horizontal
        d = math.sqrt(x**2 + y**2)

        # ángulo base
        base_angle = math.degrees(math.atan2(y, x))

        # altura (AJUSTABLE)
        z = -6   # prueba entre -5 y -8

        # cinemática
        s, e = self.inverse_kinematics(z, d)

        if self.verbose:
            print(f"\n--- {square} ---")
            print("X:", x, "Y:", y)
            print("Dist:", d)
            print("Base:", base_angle)
            print("Shoulder:", s)
            print("Elbow:", e)

        # enviar movimiento
        self.base_to(int(base_angle))
        self.combo_move(s, e)

    # ---------------- MOVIMIENTO COMPLETO ----------------

    def move(self, sq1, sq2):
        self.drop()
        self.go_to(sq1)
        self.grasp()
        self.rest()
        self.go_to(sq2)
        self.drop()
        self.rest()


# ---------------- MAIN ----------------

if __name__ == '__main__':
    robot = ChessRobotArm(26, 25, port='COM11', verbose=True)

    while True:
        sq = input("Casilla: ")
        robot.drop()
        robot.go_to(sq)
        robot.grasp()
        robot.rest()
        robot.drop()
