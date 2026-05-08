import serial
import time
import tkinter as tk

# 🔌 CAMBIA TU PUERTO
arduino = serial.Serial('COM4', 9600)  # <-- cambia esto
time.sleep(2)

# Variables de ángulo
shoulder = 90
elbow = 90
base = 90
gripper = 120

def enviar(valor):
    arduino.write((str(valor) + "\n").encode())
    print("Enviado:", valor)

def update_labels():
    label_shoulder.config(text=f"Hombro: {shoulder}")
    label_elbow.config(text=f"Codo: {elbow}")
    label_base.config(text=f"Base: {base}")
    label_gripper.config(text=f"Pinza: {gripper}")

# --- FUNCIONES ---

def move_shoulder(delta):
    global shoulder
    shoulder = max(0, min(180, shoulder + delta))
    enviar(shoulder)
    update_labels()

def move_elbow(delta):
    global elbow
    elbow = max(0, min(180, elbow + delta))
    enviar(200 + elbow)
    update_labels()

def move_base(delta):
    global base
    base = max(0, min(180, base + delta))
    enviar(400 + base)
    update_labels()

def open_gripper():
    global gripper
    gripper = min(180, gripper + 10)
    enviar(191)
    update_labels()

def close_gripper():
    global gripper
    gripper = max(0, gripper - 10)
    enviar(192)
    update_labels()

# --- INTERFAZ ---
root = tk.Tk()
root.title("Control Brazo Robot")

# Labels
label_shoulder = tk.Label(root)
label_elbow = tk.Label(root)
label_base = tk.Label(root)
label_gripper = tk.Label(root)

label_shoulder.pack()
label_elbow.pack()
label_base.pack()
label_gripper.pack()

update_labels()

# Botones
tk.Button(root, text="Hombro +", command=lambda: move_shoulder(1)).pack()
tk.Button(root, text="Hombro -", command=lambda: move_shoulder(-1)).pack()

tk.Button(root, text="Codo +", command=lambda: move_elbow(1)).pack()
tk.Button(root, text="Codo -", command=lambda: move_elbow(-1)).pack()

tk.Button(root, text="Base +", command=lambda: move_base(1)).pack()
tk.Button(root, text="Base -", command=lambda: move_base(-1)).pack()

tk.Button(root, text="Abrir Pinza", command=open_gripper).pack()
tk.Button(root, text="Cerrar Pinza", command=close_gripper).pack()

root.mainloop()
