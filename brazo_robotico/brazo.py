from sunau import AUDIO_FILE_ENCODING_ADPCM_G721

import serial
import time

arduino = serial.Serial('COM7', 9600)
time.sleep(2)

CORRECCION_CODO   =  0  # positivo aleja
CORRECCION_HOMBRO = -7.0  # positivo aleja
CORRECCION_BASE = -6.8 # positivo aleja
ARCHIVO_PUNTOS = "puntos.txt"

# ---- LEER PUNTOS DESDE ARCHIVO ----
def cargar_puntos():
    puntos = {}
    try:
        with open(ARCHIVO_PUNTOS, "r") as f:
            for linea in f:
                linea = linea.strip()
                if linea == "" or linea.startswith("#"):
                    continue
                partes = linea.split(":")
                if len(partes) == 2:
                    casilla = partes[0].strip().upper()
                    valores = partes[1].strip().split(",")
                    if len(valores) == 3:
                        puntos[casilla] = [float(v) for v in valores]
        print(f"  Puntos cargados: {len(puntos)} casillas")
    except FileNotFoundError:
        print(f"  ERROR: no se encontró '{ARCHIVO_PUNTOS}'")
    return puntos

# ---- ENVÍO SEGURO ----
def enviar(valor):
    arduino.write((str(valor) + "\n").encode())
    print("  Enviado:", valor)
    while True:
        if arduino.in_waiting:
            respuesta = arduino.readline().decode().strip()
            print("  Arduino:", respuesta)
            if respuesta == "done":
                break

# ---- OBTENER COORDENADAS (lee el archivo cada vez) ----
def obtener_punto(casilla):
    casilla = casilla.upper()
    puntos = cargar_puntos()  # ← lee el archivo en cada consulta
    if casilla in puntos:
        return puntos[casilla]
    print(f"  Casilla '{casilla}' no válida")
    return None

# ---- MOVER A CASILLA ----
def mover_a_casilla(casilla):
    punto = obtener_punto(casilla)
    if punto is None:
        return False
    base, elbow, hombro = punto
    elbow_corregido  = elbow  + CORRECCION_CODO
    hombro_corregido = hombro + CORRECCION_HOMBRO
    base_corregido = base + CORRECCION_BASE

    enviar(f"B{base_corregido},S{hombro_corregido},E{elbow_corregido}")
    return True

# ---- DOS TIPOS DE HOME ----
def ir_home_libre():
    print("  -> HOME libre (pinza abierta)")
    enviar("HOME")

def ir_home_carga():
    print("  -> HOME carga (pinza cerrada)")

# ---- SECUENCIA COMPLETA ----
def mover_pieza(origen, destino):
    print(f"\n=== MOVIMIENTO: {origen.upper()} -> {destino.upper()} ===")

    print("[1] Abriendo pinza")

    print(f"[2] Yendo a origen: {origen.upper()}")
    if not mover_a_casilla(origen):
        return

    print("[3] Agarrando pieza")
    enviar(191)

    # Antichoque antes de subir desde origen
    print("[4] Antichoque origen")
    enviar_antichoque(origen)

    print("[5] HOME carga")
    ir_home_carga()

    print(f"[6] Yendo a destino: {destino.upper()}")
    if destino == "194":
        enviar(194)
    else:
        if not mover_a_casilla(destino):
            ir_home_libre()
            return

        print("[7] Soltando pieza")
        enviar(192)

        # Antichoque antes de subir desde destino
        print("[8] Antichoque destino")
        enviar_antichoque(destino)

    print("[9] HOME libre")
    ir_home_libre()

    print("=== MOVIMIENTO COMPLETADO ===")

# ---- ANTICHOQUE SEGÚN FILA ----
def enviar_antichoque(casilla):
    fila = int(casilla[1])  # extrae el número de la casilla ej: "A3" → 3
    if fila <= 4:
        enviar(195)  # antichoque hombro filas 1-4
    else:
        enviar(196)  # antichoque codo filas 5-8




# ---- LOOP PRINCIPAL ----
print("\nBrazo robótico de ajedrez listo.")
print(f"Leyendo puntos desde: {ARCHIVO_PUNTOS}")
print("Formato: 'a1,b3' | captura: 'a1,194' | reset: 'home' | recarga: 'puntos'\n")




while True:
    entrada = input("Comando: ").strip().lower()

    if entrada == "":
        continue

    if entrada == "home":
        ir_home_libre()
        continue

    # Comando para verificar cuántos puntos están cargados
    if entrada == "puntos":
        p = cargar_puntos()
        print(f"  {len(p)} casillas cargadas:", list(p.keys()))
        continue

    if "," in entrada:
        partes = entrada.split(",")
        if len(partes) == 2:
            mover_pieza(partes[0].strip(), partes[1].strip())
        else:
            print("  Formato incorrecto. Usa: a1,b3")
    else:
        print("  Formato incorrecto. Usa: a1,b3 o a1,194")