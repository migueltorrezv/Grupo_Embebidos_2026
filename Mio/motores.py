import serial
import threading
import os
import time

s = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)

last_dist = "---"
last_event = "---"

def leer_serial():
    global last_dist, last_event
    while True:
        if s.in_waiting:
            msg = s.readline().decode().strip()
            if msg.startswith("dist:"):
                d = msg.split(":")[1]
                if d != "999":
                    last_dist = d + " cm"
                else:
                    last_dist = "sin objeto"
            elif msg in ["motor1", "motor2", "stop"]:
                last_event = msg

def mostrar():
    while True:
        os.system('clear')
        print("=" * 35)
        print("   ROBOT CONTROL - TIVA + RPi")
        print("=" * 35)
        print(f"  Distancia : {last_dist}")
        print(f"  Evento    : {last_event}")
        print("=" * 35)
        print("  Comandos:")
        print("  [0-100] → velocidad")
        print("  [b]     → buzzer")
        print("  [q]     → salir")
        print("=" * 35)
        time.sleep(0.5)

t1 = threading.Thread(target=leer_serial, daemon=True)
t2 = threading.Thread(target=mostrar, daemon=True)
t1.start()
t2.start()

try:
    while True:
        cmd = input().strip()
        if cmd == 'q':
            break
        elif cmd == 'b':
            s.write(b"buzzer\n")
            last_event = "buzzer enviado"
        else:
            try:
                spd = int(cmd)
                if 0 <= spd <= 100:
                    s.write(f"speed:{spd}\n".encode())
                    last_event = f"velocidad {spd}%"
            except:
                last_event = "comando invalido"
except KeyboardInterrupt:
    pass
finally:
    s.close()