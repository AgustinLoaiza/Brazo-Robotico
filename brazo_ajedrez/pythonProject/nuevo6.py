import serial
import time

arduino = serial.Serial('COM4', 9600)
time.sleep(2)

# ---- PUNTOS CALIBRADOS ----
puntos = {
    # FILA 1
    "A1": [174, 29, 81],
    "B1": [164, 23, 82],
    "C1": [147, 15.5, 93],
    "D1": [126, 12, 100],
    "E1": [94, 12, 104],
    "F1": [71, 18, 95],
    "G1": [61.5, 25, 84],
    "H1": [53, 35, 79],

    # FILA 2
    "A2": [164, 37, 74],
    "B2": [153.5, 29, 80],
    "C2": [139.5, 26, 88],
    "D2": [123, 20, 92],
    "E2": [100.5, 21, 86],
    "F2": [85, 25, 83],
    "G2": [72.5, 34, 77],
    "H2": [61, 41, 70],

    # FILA 3
    "A3": [155, 45, 67],
    "B3": [146.5, 39, 72],
    "C3": [134.5, 35, 76],
    "D3": [123, 30.5, 76],
    "E3": [106, 30, 78],
    "F3": [91, 34, 75],
    "G3": [89.5, 33, 76],
    "H3": [73, 45, 66],

    # FILA 4
    "A4": [149.5, 48, 62],
    "B4": [142, 44, 66],
    "C4": [132, 41.5, 67],
    "D4": [120, 41.5, 69.5],
    "E4": [108.5, 39, 69],
    "F4": [97, 42, 65.5],
    "G4": [87, 46, 64],
    "H4": [76.5, 53.5, 59],

    # FILA 5
    "A5": [144, 59, 54],
    "B5": [135, 55.5, 58],
    "C5": [129, 52, 60],
    "D5": [120.5, 49.5, 61.5],
    "E5": [108, 49, 61],
    "F5": [98.5, 50, 61],
    "G5": [91, 54, 58],
    "H5": [82.5, 62, 53],

    # FILA 6
    "A6": [140.5, 70, 48],
    "B6": [133, 66.5, 49],
    "C6": [125, 62, 50.5],
    "D6": [119, 61, 53],
    "E6": [108.5, 62, 51.5],
    "F6": [101.2, 64.5, 51.1],
    "G6": [93, 66.4, 48.7],
    "H6": [86.3, 73, 46.1],

    # FILA 7
    "A7": [138.6, 83.9, 39],
    "B7": [131.6, 82.2, 39.5],
    "C7": [125.1, 77.3, 43.2],
    "D7": [117.1, 78, 42.7],
    "E7": [112.2, 76.8, 43],
    "F7": [103.2, 77, 41],
    "G7": [96.4, 81.5, 40],
    "H7": [89.8, 85.4, 37.7],

    # FILA 8
    "A8": [136.8, 99, 27.7],
    "B8": [130.8, 96.5, 29],
    "C8": [124.6, 92, 33],
    "D8": [116.5, 91, 33],
    "E8": [110.3, 92, 33],
    "F8": [103.7, 92, 33],
    "G8": [97, 95.5, 31],
    "H8": [91, 102, 26.5],
}
# ---- POSICIÓN INICIAL ----
HOME = [120, 90, 90]

# ---- ENVÍO SEGURO ----
def enviar(valor):
    arduino.write((str(valor) + "\n").encode())
    print("Enviado:", valor)

    while True:
        if arduino.in_waiting:
            respuesta = arduino.readline().decode().strip()
            print("Arduino:", respuesta)
            if respuesta == "done":
                break

# ---- USAR PUNTOS DIRECTOS (SIN INTERPOLACIÓN) ----
def obtener_punto(casilla):
    if casilla in puntos:
        return puntos[casilla]
    else:
        print("Casilla no válida")
        return None, None, None

# ---- MOVER BRAZO (TU FORMA ORIGINAL) ----
def mover_servos(base, codo, hombro):
    enviar(400 + base)
    enviar(200 + codo)
    enviar(hombro)

def mover_servos1(base, codo, hombro):
    enviar(hombro)
    enviar(200 + codo)
    enviar(400 + base)

# ---- IR A HOME ----
def ir_home():
    print("\nVolviendo a HOME")
    mover_servos1(HOME[0], HOME[1], HOME[2])

# ---- SECUENCIA COMPLETA ----
def mover_a(casilla):
    base, codo, hombro = obtener_punto(casilla)

    if base is None:
        return

    print(f"\nMoviendo a {casilla}")
    print(base, codo, hombro)

    # Abrir pinza
    enviar(192)

    # Ir directo arriba de la casilla (sin barrer lateral)
    mover_servos(base, codo, hombro)

    time.sleep(0.5)

    # Cerrar pinza
    enviar(191)

    time.sleep(0.5)

    # Volver
    ir_home()

# ---- LOOP ----
while True:
    destino = input("\nCasilla (ej: A1): ").upper()
    mover_a(destino)