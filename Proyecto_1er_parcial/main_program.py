import threading
import time

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO_AVAILABLE = True
except:
    GPIO_AVAILABLE = False

from model_a import ModelA
from model_b import ModelB

class RobotController:
    def __init__(self):
        self.current_model = None
        self.model_index = 0
        self.models_names = ["Model A", "Model B"]
        self.running = True
        self._btn_prev = True

    def _create_model(self, index):
        if index == 0:
            return ModelA()
        elif index == 1:
            return ModelB()

    def _run_model(self, model):
        t = threading.Thread(target=model.run, daemon=True)
        t.start()
        return t

    def switch_model(self):
        print(f"\n[SWITCH] Cambiando modelo...")
        if self.current_model:
            self.current_model.stop()
            time.sleep(0.5)
        self.model_index = (self.model_index + 1) % len(self.models_names)
        self.current_model = self._create_model(self.model_index)
        self._run_model(self.current_model)
        print(f"[SWITCH] Activo: {self.models_names[self.model_index]}")

    def _monitor_button(self):
        while self.running:
            if GPIO_AVAILABLE:
                btn = GPIO.input(26)
                if not btn and self._btn_prev:
                    time.sleep(0.05)
                    if not GPIO.input(26):
                        self.switch_model()
                self._btn_prev = btn
            time.sleep(0.05)

    def run(self):
        print("=" * 40)
        print("   ROBOT CONTROLLER")
        print("=" * 40)
        print("A=autonomo, B=teclado")
        print("Boton GPIO26 cambia modelo")
        print("Ctrl+C salir")
        print("=" * 40)

        self.current_model = self._create_model(self.model_index)
        self._run_model(self.current_model)
        print(f"[INICIO] {self.models_names[self.model_index]} activo")

        t_btn = threading.Thread(target=self._monitor_button, daemon=True)
        t_btn.start()

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nCerrando...")
            if self.current_model:
                self.current_model.stop()
            if GPIO_AVAILABLE:
                GPIO.cleanup()

if __name__ == "__main__":
    robot = RobotController()
    robot.run()
'''
pip install readchar --break-system-packages
python3 main_program.py
'''
