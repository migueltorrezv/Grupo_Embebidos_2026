import tkinter as tk
import serial

# --- VARIABLES GLOBALES ---
s = None
vel1_timer = None
vel2_timer = None

# Paleta de colores
BG = "#0d0d0d"
PANEL = "#1a1a2e"
ACCENT = "#e94560"
GREEN = "#00b4d8"
YELLOW = "#ffd60a"
WHITE = "#ffffff"
GRAY = "#aaaaaa"

# --- CONEXIÓN SERIAL ---
# IMPORTANTE: Cambia '/dev/ttyACM0' (Linux/Mac) o 'COM3' (Windows) según tu PC.
PUERTO = '/dev/ttyACM0' 

try:
    s = serial.Serial(PUERTO, 115200, timeout=0.1)
    print(f"✅ Conectado a {PUERTO}")
except Exception as e:
    print(f"❌ Error al abrir el puerto serial: {e}")
    print("La interfaz se abrirá en modo prueba (sin conexión real).")

# --- FUNCIÓN DE LECTURA SEGURA (SIN THREADS) ---
def check_serial():
    if s and s.is_open:
        try:
            while s.in_waiting > 0:
                # Se añade errors='ignore' por si llega ruido por el serial
                msg = s.readline().decode('utf-8', errors='ignore').strip()
                if not msg:
                    continue
                
                # Parseo de mensajes enviados por la Tiva-C
                if msg.startswith("dist:"):
                    d = msg.split(":")[1]
                    if d == "999" or d == "0":
                        lbl_dist.config(text="--- cm", fg=GRAY)
                    else:
                        lbl_dist.config(text=f"{d} cm", fg=GREEN)
                
                elif msg == "stop":
                    lbl_evento.config(text="⚠ STOP - objeto detectado", fg=ACCENT)
                    btn_m1.config(bg="#333", text="Motor 1  OFF")
                    btn_m2.config(bg="#333", text="Motor 2  OFF")
                
                elif msg == "motor1:on":
                    btn_m1.config(bg=GREEN, text="Motor 1  ON")
                    lbl_evento.config(text="Motor 1 activado", fg=GREEN)
                elif msg == "motor1:off":
                    btn_m1.config(bg="#333", text="Motor 1  OFF")
                
                elif msg == "motor2:on":
                    btn_m2.config(bg=GREEN, text="Motor 2  ON")
                    lbl_evento.config(text="Motor 2 activado", fg=GREEN)
                elif msg == "motor2:off":
                    btn_m2.config(bg="#333", text="Motor 2  OFF")
                    
        except Exception as e:
            print(f"Error procesando datos: {e}")
            
    # Tkinter vuelve a llamar a esta función cada 50 milisegundos
    root.after(50, check_serial)

# --- FUNCIONES DE ENVÍO DE COMANDOS ---
def toggle_motor1():
    if s and s.is_open:
        s.write(b"motor1\n")

def toggle_motor2():
    if s and s.is_open:
        s.write(b"motor2\n")

def enviar_velocidad1(val):
    global vel1_timer
    spd = int(float(val))
    lbl_vel1.config(text=f"Velocidad M1: {spd}%")
    if vel1_timer:
        root.after_cancel(vel1_timer)
    if s and s.is_open:
        vel1_timer = root.after(200, lambda: s.write(f"speed1:{spd}\n".encode()))

def enviar_velocidad2(val):
    global vel2_timer
    spd = int(float(val))
    lbl_vel2.config(text=f"Velocidad M2: {spd}%")
    if vel2_timer:
        root.after_cancel(vel2_timer)
    if s and s.is_open:
        vel2_timer = root.after(200, lambda: s.write(f"speed2:{spd}\n".encode()))

def enviar_buzzer():
    if s and s.is_open:
        s.write(b"buzzer\n")
    lbl_evento.config(text="🔔 Buzzer activado", fg=YELLOW)

# --- CONFIGURACIÓN DE LA INTERFAZ GRÁFICA ---
root = tk.Tk()
root.title("Robot Control Panel")
root.geometry("420x680")
root.configure(bg=BG)
root.resizable(False, False)

tk.Label(root, text="🤖 ROBOT CONTROL", font=("Helvetica", 20, "bold"),
         bg=BG, fg=WHITE).pack(pady=15)

# Panel de Distancia
frame_dist = tk.Frame(root, bg=PANEL, bd=0)
frame_dist.pack(fill="x", padx=20, pady=5)
tk.Label(frame_dist, text="DISTANCIA", font=("Helvetica", 10), bg=PANEL, fg=GRAY).pack(pady=(10,0))
lbl_dist = tk.Label(frame_dist, text="--- cm", font=("Helvetica", 36, "bold"), bg=PANEL, fg=GREEN)
lbl_dist.pack(pady=(0,10))

# Eventos
lbl_evento = tk.Label(root, text="Sistema listo", font=("Helvetica", 11), bg=BG, fg=GRAY)
lbl_evento.pack(pady=5)

# Panel de Motores (Botones)
frame_motors = tk.Frame(root, bg=BG)
frame_motors.pack(pady=10)
btn_m1 = tk.Button(frame_motors, text="Motor 1  OFF", font=("Helvetica", 13, "bold"),
                   bg="#333", fg=WHITE, width=14, height=2, relief="flat", cursor="hand2", command=toggle_motor1)
btn_m1.grid(row=0, column=0, padx=10)

btn_m2 = tk.Button(frame_motors, text="Motor 2  OFF", font=("Helvetica", 13, "bold"),
                   bg="#333", fg=WHITE, width=14, height=2, relief="flat", cursor="hand2", command=toggle_motor2)
btn_m2.grid(row=0, column=1, padx=10)

# Panel de Velocidades (Sliders)
frame_vel = tk.Frame(root, bg=PANEL)
frame_vel.pack(fill="x", padx=20, pady=10)

tk.Label(frame_vel, text="VELOCIDAD MOTOR 1", font=("Helvetica", 10), bg=PANEL, fg=GRAY).pack(pady=(10,0))
lbl_vel1 = tk.Label(frame_vel, text="Velocidad M1: 50%", font=("Helvetica", 12, "bold"), bg=PANEL, fg=WHITE)
lbl_vel1.pack()
slider1 = tk.Scale(frame_vel, from_=0, to=100, orient=tk.HORIZONTAL, length=340, bg=PANEL, fg=WHITE, 
                   troughcolor="#333", highlightbackground=PANEL, activebackground=ACCENT, command=enviar_velocidad1)
slider1.set(50)
slider1.pack(pady=(0,10))

tk.Label(frame_vel, text="VELOCIDAD MOTOR 2", font=("Helvetica", 10), bg=PANEL, fg=GRAY).pack(pady=(5,0))
lbl_vel2 = tk.Label(frame_vel, text="Velocidad M2: 50%", font=("Helvetica", 12, "bold"), bg=PANEL, fg=WHITE)
lbl_vel2.pack()
slider2 = tk.Scale(frame_vel, from_=0, to=100, orient=tk.HORIZONTAL, length=340, bg=PANEL, fg=WHITE, 
                   troughcolor="#333", highlightbackground=PANEL, activebackground=ACCENT, command=enviar_velocidad2)
slider2.set(50)
slider2.pack(pady=(0,10))

# Botón Buzzer
tk.Button(root, text="🔔  BUZZER", font=("Helvetica", 14, "bold"),
          bg=ACCENT, fg=WHITE, width=20, height=2, relief="flat", cursor="hand2", command=enviar_buzzer).pack(pady=15)

# --- INICIO DEL PROGRAMA ---
# Arranca el loop seguro para leer el serial
root.after(50, check_serial)

# Arranca la ventana de Tkinter
root.mainloop()

# Cierra el puerto al cerrar la ventana
if s and s.is_open:
    s.close()