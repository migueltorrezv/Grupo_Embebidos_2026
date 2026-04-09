import tkinter as tk
import serial
import threading

s = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

BG = "#0d0d0d"
PANEL = "#1a1a2e"
ACCENT = "#e94560"
GREEN = "#00b4d8"
YELLOW = "#ffd60a"
WHITE = "#ffffff"
GRAY = "#aaaaaa"

loop_cmd = None

def enviar(cmd):
    s.write((cmd + "\n").encode())

def presionar(cmd):
    enviar(cmd)
    global loop_cmd
    loop_cmd = root.after(100, lambda: presionar(cmd))

def soltar(event=None):
    global loop_cmd
    if loop_cmd:
        root.after_cancel(loop_cmd)
    enviar("st")

def leer_serial():
    while True:
        if s.in_waiting:
            msg = s.readline().decode().strip()
            root.after(0, procesar, msg)

def procesar(msg):
    if msg.startswith("dist:"):
        lbl_dist.config(text=msg.split(":")[1] + " cm")
    elif msg == "stop":
        lbl_evento.config(text="⚠ STOP")

root = tk.Tk()
root.title("Robot")
root.geometry("400x550")
root.configure(bg=BG)

lbl_dist = tk.Label(root, text="---", font=("Helvetica", 30), fg=GREEN, bg=BG)
lbl_dist.pack()

lbl_evento = tk.Label(root, text="Listo", fg=GRAY, bg=BG)
lbl_evento.pack()

frame = tk.Frame(root, bg=BG)
frame.pack(pady=20)

def bind_btn(btn, cmd):
    btn.bind("<ButtonPress>", lambda e: presionar(cmd))
    btn.bind("<ButtonRelease>", soltar)

btn_up = tk.Button(frame, text="↑", width=5, height=2)
btn_up.grid(row=0, column=1)
bind_btn(btn_up, "f")

btn_left = tk.Button(frame, text="←", width=5, height=2)
btn_left.grid(row=1, column=0)
bind_btn(btn_left, "l")

btn_right = tk.Button(frame, text="→", width=5, height=2)
btn_right.grid(row=1, column=2)
bind_btn(btn_right, "r")

btn_down = tk.Button(frame, text="↓", width=5, height=2)
btn_down.grid(row=2, column=1)
bind_btn(btn_down, "back")

slider = tk.Scale(root, from_=0, to=100, orient="horizontal",
                  command=lambda v: enviar(f"speed:{int(v)}"))
slider.set(50)
slider.pack()

tk.Button(root, text="Buzzer", command=lambda: enviar("buzzer")).pack(pady=10)

threading.Thread(target=leer_serial, daemon=True).start()

root.mainloop()
s.close()