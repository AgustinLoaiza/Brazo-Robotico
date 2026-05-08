import serial
import time
import numpy as np

# ------------------ CONFIG ------------------
puerto = "COM4"
baud = 9600
arduino = serial.Serial(puerto, baud, timeout=1)
time.sleep(2)

# ------------------ PINZA ------------------
PINZA_ABRIR = 191
PINZA_CERRAR = 192

# ------------------ POSICIÓN INICIAL ------------------
home = [90, 90, 90]

# ------------------ PUNTOS CALIBRADOS ------------------
puntos = {
    "A1": [174, 29, 81],
    "A8": [137.5, 94, 28],
    "H8": [93, 98, 26],
    "H1": [48.5, 33, 79],

    # 🔥 TUS PUNTOS IMPORTANTES
    "E1": [89, 11, 106],
    "E8": [109, 95, 37]
}

# ------------------ ENVIAR AL ARDUINO ------------------
def enviar(base, hombro, codo):
    base = int(base - 200)
    hombro = int(hombro - 200)
    codo = int(codo - 400)

    comando = f"{base},{hombro},{codo}\n"
    arduino.write(comando.encode())
    print("Enviado:", comando.strip())
    time.sleep(0.4)

def pinza(accion):
    arduino.write(f"{accion}\n".encode())
    time.sleep(0.6)

# ------------------ INTERPOLACIÓN MEJORADA ------------------
def interpolar(x, y):
    """
    x = columna (0 a 7)
    y = fila (0 a 7)
    """

    # Bordes
    A1 = np.array(puntos["A1"])
    A8 = np.array(puntos["A8"])
    H1 = np.array(puntos["H1"])
    H8 = np.array(puntos["H8"])

    # Interpolación base (bilineal)
    abajo = A1 + (H1 - A1) * (x / 7)
    arriba = A8 + (H8 - A8) * (x / 7)
    punto = abajo + (arriba - abajo) * (y / 7)

    # 🔥 Corrección usando E1 y E8
    if x == 4:  # columna E
        E1 = np.array(puntos["E1"])
        E8 = np.array(puntos["E8"])
        punto = E1 + (E8 - E1) * (y / 7)

    return punto

# ------------------ CONVERTIR CASILLA ------------------
def casilla_a_coord(casilla):
    col = ord(casilla[0]) - ord('A')
    fila = int(casilla[1]) - 1
    return interpolar(col, fila)

# ------------------ MOVIMIENTO SUAVE ------------------
def mover_suave(inicio, fin, pasos=15):
    for i in range(pasos + 1):
        t = i / pasos
        punto = inicio + (fin - inicio) * t
        enviar(punto[0], punto[1], punto[2])

# ------------------ MOVIMIENTO NATURAL ------------------
def mover_pieza(origen, destino):
    print(f"\nMoviendo de {origen} a {destino}")

    p_origen = casilla_a_coord(origen)
    p_destino = casilla_a_coord(destino)

    altura = np.array([0, 0, 40])  # subir vertical

    arriba_origen = p_origen + altura
    arriba_destino = p_destino + altura

    # 1. ir arriba origen
    mover_suave(np.array(home), arriba_origen)

    # 2. abrir pinza
    pinza(PINZA_ABRIR)

    # 3. bajar
    mover_suave(arriba_origen, p_origen)

    # 4. cerrar pinza
    pinza(PINZA_CERRAR)

    # 5. subir
    mover_suave(p_origen, arriba_origen)

    # 6. ir arriba destino
    mover_suave(arriba_origen, arriba_destino)

    # 7. bajar
    mover_suave(arriba_destino, p_destino)

    # 8. abrir pinza (soltar)
    pinza(PINZA_ABRIR)

    # 9. subir
    mover_suave(p_destino, arriba_destino)

    # 10. volver a casa
    mover_suave(arriba_destino, np.array(home))

# ------------------ PRUEBA ------------------
mover_pieza("E2", "E4")