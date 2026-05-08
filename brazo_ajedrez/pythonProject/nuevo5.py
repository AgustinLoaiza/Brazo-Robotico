import serial
import time

arduino = serial.Serial('COM11', 9600)
time.sleep(2)

# ---- PUNTOS ----
puntos = {
    "A1": [174, 29, 81],
    "A8": [136, 99.5, 26.5],
    "H8": [93, 99, 26],
    "H1": [48.5, 33, 79]
}

HOME = [120, 90, 90]

# ---- ENVÍO ----
def enviar(valor):
    arduino.write((str(valor) + "\n").encode())
    print("Enviado:", valor)

    while True:
        if arduino.in_waiting:
            r = arduino.readline().decode().strip()
            if r == "done":
                break

# ---- INTERPOLACIÓN (TUYA) ----
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

# ---- MOVIMIENTOS SEGUROS ----

def subir(hombro):
    enviar(hombro - 25)  # sube brazo

def bajar(hombro):
    enviar(hombro)       # baja brazo

def mover_base(base):
    enviar(400 + base)

def mover_codo(codo):
    enviar(200 + codo)

# ---- IR A HOME ----
def ir_home():
    print("\nVolviendo a HOME")
    enviar(HOME[2])         # hombro
    enviar(200 + HOME[1])   # codo
    enviar(400 + HOME[0])   # base

# ---- MOVIMIENTO REAL ----
def mover_a(casilla):
    col = ord(casilla[0]) - ord('A')
    fila = int(casilla[1]) - 1

    base, codo, hombro = interpolar(col, fila)

    print(f"{casilla} ->", base, codo, hombro)

    # 1️⃣ SUBIR
    subir(hombro)
    time.sleep(0.3)

    # 2️⃣ MOVER BASE (sin chocar)
    mover_base(base)
    time.sleep(0.3)

    # 3️⃣ AJUSTAR CODO
    mover_codo(codo)
    time.sleep(0.3)

    # 4️⃣ ABRIR PINZA
    enviar(192)
    time.sleep(0.3)

    # 5️⃣ BAJAR
    bajar(hombro)
    time.sleep(0.4)

    # 6️⃣ CERRAR PINZA
    enviar(191)
    time.sleep(0.5)

    # 7️⃣ SUBIR OTRA VEZ
    subir(hombro)
    time.sleep(0.3)

    # 8️⃣ VOLVER
    ir_home()

# ---- LOOP ----
while True:
    destino = input("Casilla: ").upper()
    mover_a(destino)