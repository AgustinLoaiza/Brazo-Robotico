import serial
import time

arduino = serial.Serial('COM4', 9600)
time.sleep(2)

# ---- PUNTOS CALIBRADOS ----
puntos = {
    "A1": [174, 29, 81],
    "A8": [136, 99.5, 26.5],
    "H8": [93, 99, 26],
    "H1": [48.5, 33, 79]
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

# ---- CINEMÁTICA (INTERPOLACIÓN) ----
def interpolar(x, y):
    base_abajo = puntos["A1"][0] + (puntos["H1"][0] - puntos["A1"][0]) * (x / 7)
    base_arriba = puntos["A8"][0] + (puntos["H8"][0] - puntos["A8"][0]) * (x / 7)

    codo_abajo = puntos["A1"][1] + (puntos["H1"][1] - puntos["A1"][1]) * (x / 7)
    codo_arriba = puntos["A8"][1] + (puntos["H8"][1] - puntos["A8"][1]) * (x / 7)

    hombro_abajo = puntos["A1"][2] + (puntos["H1"][2] - puntos["A1"][2]) * (x / 7)
    hombro_arriba = puntos["A8"][2] + (puntos["H8"][2] - puntos["A8"][2]) * (x / 7)

    base = base_abajo + (base_arriba - base_abajo) * (y / 7)
    codo = codo_abajo + (codo_arriba - codo_abajo) * (y / 7)
    hombro = hombro_abajo + (hombro_arriba - hombro_abajo) * (y / 7)

    return int(base), int(codo), int(hombro)

# ---- MOVER BRAZO ----
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
    col = ord(casilla[0]) - ord('A')
    fila = int(casilla[1]) - 1

    base, codo, hombro = interpolar(col, fila)

    print(f"\nMoviendo a {casilla}")
    print(base, codo, hombro)

    # 1️⃣ Abrir pinza antes de llegar
    enviar(192)

    # 2️⃣ Ir a la posición
    mover_servos(base, codo, hombro)

    time.sleep(0.5)

    # 3️⃣ Cerrar pinza
    enviar(191)

    time.sleep(0.5)

    # 4️⃣ Volver a casa
    ir_home()

# ---- LOOP ----
while True:
    destino = input("\nCasilla (ej: A1): ").upper()
    mover_a(destino)
