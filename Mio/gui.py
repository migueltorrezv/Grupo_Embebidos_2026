import tkinter as tk
import serial
import threading

s = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

motor1_on = False
motor2_on = False
vel_timer = None

BG = "#0d0d0d"
PANEL = "#1a1a2e"
ACCENT = "#e94560"
GREEN = "#00b4d8"
YELLOW = "#ffd60a"
WHITE = "#ffffff"
GRAY = "#aaaaaa"

def leer_serial():
    while True:
        if s.in_waiting:
            msg = s.readline().decode().strip()
            if msg.startswith("dist:"):
                d = msg.split(":")[1]
                if d == "999":
                    lbl_dist.config(text="--- cm", fg=GRAY)
                else:
                    lbl_dist.config(text=f"{d} cm", fg=GREEN)
            elif msg == "stop":
                lbl_evento.config(text="⚠ STOP - objeto detectado", fg=ACCENT)
                btn_m1.config(bg="#333", text="Motor 1  OFF")
                btn_m2.config(bg="#333", text="Motor 2  OFF")
            elif msg == "motor1:on":
                btn_m1.config(bg=GREEN, text="Motor 1  ON")
            elif msg == "motor1:off":
                btn_m1.config(bg="#333", text="Motor 1  OFF")
            elif msg == "motor2:on":
                btn_m2.config(bg=GREEN, text="Motor 2  ON")
            elif msg == "motor2:off":
                btn_m2.config(bg="#333", text="Motor 2  OFF")

def toggle_motor1():
    s.write(b"motor1\n")

def toggle_motor2():
    s.write(b"motor2\n")

def enviar_velocidad(val):
    global vel_timer
    spd = int(float(val))
    lbl_vel.config(text=f"Velocidad: {spd}%")
    if vel_timer:
        root.after_cancel(vel_timer)
    vel_timer = root.after(300, lambda: s.write(f"speed:{spd}\n".encode()))

def enviar_buzzer():
    s.write(b"buzzer\n")
    lbl_evento.config(text="🔔 Buzzer activado", fg=YELLOW)

root = tk.Tk()
root.title("Robot Control Panel")
root.geometry("420x600")
root.configure(bg=BG)
root.resizable(False, False)

tk.Label(root, text="🤖 ROBOT CONTROL", font=("Helvetica", 20, "bold"),
         bg=BG, fg=WHITE).pack(pady=15)

frame_dist = tk.Frame(root, bg=PANEL, bd=0)
frame_dist.pack(fill="x", padx=20, pady=5)
tk.Label(frame_dist, text="DISTANCIA", font=("Helvetica", 10),
         bg=PANEL, fg=GRAY).pack(pady=(10,0))
lbl_dist = tk.Label(frame_dist, text="--- cm", font=("Helvetica", 36, "bold"),
                    bg=PANEL, fg=GREEN)
lbl_dist.pack(pady=(0,10))

lbl_evento = tk.Label(root, text="Sistema listo", font=("Helvetica", 11),
                      bg=BG, fg=GRAY)
lbl_evento.pack(pady=5)

frame_motors = tk.Frame(root, bg=BG)
frame_motors.pack(pady=10)

btn_m1 = tk.Button(frame_motors, text="Motor 1  OFF", font=("Helvetica", 13, "bold"),
                   bg="#333", fg=WHITE, width=14, height=2,
                   relief="flat", cursor="hand2", command=toggle_motor1)
btn_m1.grid(row=0, column=0, padx=10)

btn_m2 = tk.Button(frame_motors, text="Motor 2  OFF", font=("Helvetica", 13, "bold"),
                   bg="#333", fg=WHITE, width=14, height=2,
                   relief="flat", cursor="hand2", command=toggle_motor2)
btn_m2.grid(row=0, column=1, padx=10)

frame_vel = tk.Frame(root, bg=PANEL)
frame_vel.pack(fill="x", padx=20, pady=10)
tk.Label(frame_vel, text="VELOCIDAD", font=("Helvetica", 10),
         bg=PANEL, fg=GRAY).pack(pady=(10,0))
lbl_vel = tk.Label(frame_vel, text="Velocidad: 50%", font=("Helvetica", 14, "bold"),
                   bg=PANEL, fg=WHITE)
lbl_vel.pack()
slider = tk.Scale(frame_vel, from_=0, to=100, orient=tk.HORIZONTAL,
                  length=340, bg=PANEL, fg=WHITE, troughcolor="#333",
                  highlightbackground=PANEL, activebackground=ACCENT,
                  command=enviar_velocidad)
slider.set(50)
slider.pack(pady=(0,10))

tk.Button(root, text="🔔  BUZZER", font=("Helvetica", 14, "bold"),
          bg=ACCENT, fg=WHITE, width=20, height=2,
          relief="flat", cursor="hand2", command=enviar_buzzer).pack(pady=15)

t = threading.Thread(target=leer_serial, daemon=True)
t.start()

root.mainloop()
s.close()
