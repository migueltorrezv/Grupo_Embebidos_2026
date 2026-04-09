import serial
import threading
import time

try:
    import readchar
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "readchar", "--break-system-packages"])
    import readchar

class ModelB:
    def __init__(self, port='/dev/ttyACM0', baud=115200):
        self.s = serial.Serial(port, baud, timeout=0.1)
        self.running = False
        self.dist = 999
        self.nitro = False
        self.current_cmd = "stop"
        self._lock = threading.Lock()

    def send(self, cmd):
        with self._lock:
            self.s.write(f"{cmd}\n".encode())

    def _leer_serial(self):
        while self.running:
            if self.s.in_waiting:
                msg = self.s.readline().decode().strip()
                if msg.startswith("dist:"):
                    try:
                        self.dist = int(msg.split(":")[1])
                    except:
                        pass

    def _safety_check(self):
        while self.running:
            if self.dist > 0 and self.dist <= 5:
                self.send("stop")
            time.sleep(0.1)

    def toggle_nitro(self):
        self.nitro = not self.nitro
        if self.nitro:
            self.send("speed:100")
            print("NITRO ON")
        else:
            self.send("speed:70")
            print("NITRO OFF")

    def run(self):
        self.running = True
        t1 = threading.Thread(target=self._leer_serial, daemon=True)
        t2 = threading.Thread(target=self._safety_check, daemon=True)
        t1.start()
        t2.start()
        self.send("speed:70")
        print("Model B activo — W/A/S/D=direccion, N=nitro, Q=salir")

        try:
            while self.running:
                key = readchar.readkey().lower()
                if key == 'w':
                    self.send("forward")
                elif key == 's':
                    self.send("backward")
                elif key == 'a':
                    self.send("left")
                elif key == 'd':
                    self.send("right")
                elif key == 'n':
                    self.toggle_nitro()
                elif key == ' ':
                    self.send("stop")
                elif key == 'q':
                    self.stop()
                    break
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.send("stop")
        self.s.close()
