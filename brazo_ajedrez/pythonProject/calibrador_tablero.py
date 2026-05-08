import tkinter as tk
from arm import ChessRobotArm

# ===============================
# CONFIGURACIÓN DEL ROBOT
# ===============================
PORT = 'COM4'
ARM_A = 20
ARM_B = 27

robot = ChessRobotArm(ARM_A, ARM_B, port=PORT, verbose=True)

# ===============================
# INTERFAZ GRÁFICA






# ===============================
root = tk.Tk()
root.title("Calibración – Robot Ajedrez")
root.resizable(False, False)

# ===============================
# FUNCIÓN DE MOVIMIENTO
# ===============================
def mover(square):
    print("Moviendo a:", square)
    robot.go_to_square_only(square)

# ===============================
# TABLERO 8x8
# ===============================
files = ['a','b','c','d','e','f','g','h']
ranks = [8,7,6,5,4,3,2,1]

for row, r in enumerate(ranks):
    for col, f in enumerate(files):
        square = f + str(r)
        color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"

        btn = tk.Button(
            root,
            text=square.upper(),
            width=6,
            height=3,
            bg=color,
            fg="black",
            font=("Arial", 10, "bold"),
            command=lambda s=square: mover(s)
        )
        btn.grid(row=row, column=col)

# ===============================
# BOTONES EXTRA
# ===============================
def reposo():
    robot.rest()

def abrir():
    robot.drop()

def cerrar():
    robot.grasp()

tk.Button(root, text="REPOSO", width=15, command=reposo).grid(row=8, column=0, columnspan=2)
tk.Button(root, text="ABRIR",  width=15, command=abrir ).grid(row=8, column=2, columnspan=2)
tk.Button(root, text="CERRAR", width=15, command=cerrar).grid(row=8, column=4, columnspan=2)

root.mainloop()
