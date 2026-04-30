import serial
import threading
import time

class ModelA:
    def __init__(self, port='/dev/ttyACM0', baud=115200):
        self.s = serial.Serial(port, baud, timeout=0.1)
        self.running = False
        self.dist = 999
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

    def turn(self, degrees, direction="right"):
        def _do_turn():
            t = (degrees / 360) * 2.0
            self.send(direction)
            time.sleep(t)
            self.send("forward")
        threading.Thread(target=_do_turn, daemon=True).start()

    def run(self):
        self.running = True
        self.send("forward")
        t = threading.Thread(target=self._leer_serial, daemon=True)
        t.start()

        try:
            while self.running:
                if self.dist > 0 and self.dist <= 5:
                    self.send("stop")
                    time.sleep(0.5)
                    self.turn(180, "right")
                    time.sleep(2.5)
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.send("stop")
        self.s.close()
Sí, el `main_program.py` debe arrancar solo en modo autónomo (Model A) sin esperar órdenes. El robot debe:

1. Arrancar → modo autónomo automáticamente
2. Botón GPIO26 → cambia a Model B (teclado)
3. Botón GPIO26 de nuevo → vuelve a Model A

El `main_program.py` ya hace eso — arranca con `model_index = 0` que es Model A.

¿Está compilando y flasheando bien la TIVA ahora?
