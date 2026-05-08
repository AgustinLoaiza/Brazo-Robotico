import serial
import time
import tkinter as tk

# CONFIGURAR PUERTO
arduino = serial.Serial('COM4', 9600)
time.sleep(2)

# ---------------- FUNCIONES ----------------

def mover_base(valor):
    dato = 400 + valor
    arduino.write((str(dato) + "\n").encode())

def mover_hombro(valor):
    arduino.write((str(valor) + "\n").encode())

def mover_combo():
    s = int(scale_hombro.get())
    e = int(scale_codo.get())

    # activar modo combo
    arduino.write((str(200 + e) + "\n").encode())
    time.sleep(0.3)
    arduino.write((str(s) + "\n").encode())

def abrir_pinza():
    arduino.write(b"191\n")

def cerrar_pinza():
    arduino.write(b"192\n")

def reset():
    arduino.write(b"190\n")

# ---------------- INTERFAZ ----------------

root = tk.Tk()
root.title("Control Robot")

# BASE
tk.Label(root, text="Base").pack()
scale_base = tk.Scale(root, from_=0, to=180, orient=tk.HORIZONTAL, command=lambda x: mover_base(int(x)))
scale_base.pack()

# HOMBRO
tk.Label(root, text="Hombro").pack()
scale_hombro = tk.Scale(root, from_=0, to=180, orient=tk.HORIZONTAL)
scale_hombro.pack()

# CODO
tk.Label(root, text="Codo").pack()
scale_codo = tk.Scale(root, from_=0, to=180, orient=tk.HORIZONTAL)
scale_codo.pack()

# BOTON COMBO
tk.Button(root, text="Mover Hombro + Codo", command=mover_combo).pack(pady=10)

# PINZA
tk.Button(root, text="Abrir Pinza", command=abrir_pinza).pack()
tk.Button(root, text="Cerrar Pinza", command=cerrar_pinza).pack()

# RESET
tk.Button(root, text="Posición Inicial", command=reset).pack(pady=10)

root.mainloop()
