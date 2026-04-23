import serial
import threading
import time

try:
    import RPi.GPIO as GPIO
    _GPIO_AVAILABLE = True
except ImportError:
    _GPIO_AVAILABLE = False
    print("[WARN] RPi.GPIO no disponible – botón físico deshabilitado")

from model_a import ModelA
from model_b import ModelB


class RobotController:
    """
    Controlador central. Gestiona ModelA y ModelB.
    Botón físico en GPIO26 (RPi) alterna entre modos.
    Toda la lógica de cambio corre en threads separados.
    """

    BUTTON_PIN   = 26
    DEBOUNCE_MS  = 300
    SERIAL_PORT  = '/dev/ttyACM0'
    BAUD_RATE    = 115200

    def __init__(self):
        self._serial  = serial.Serial(self.SERIAL_PORT, self.BAUD_RATE, timeout=0.1)
        self._model_a = ModelA(self._serial)
        self._model_b = ModelB(self._serial)

        # Asignar callbacks compartidos
        self._model_a.on_distance = self._on_distance
        self._model_a.on_event    = self._on_event
        self._model_b.on_distance = self._on_distance
        self._model_b.on_event    = self._on_event

        self._active_model  = None
        self._mode          = 0          # 0 = ModelA, 1 = ModelB
        self._running       = False
        self._switch_lock   = threading.Lock()
        self._last_btn_time = 0.0

    # ------------------------------------------------------------------ #
    #  Callbacks (punteros a función)                                      #
    # ------------------------------------------------------------------ #

    def _on_distance(self, dist: int) -> None:
        label = "sin objeto" if dist == 999 else f"{dist} cm"
        print(f"[DIST]  {label}")

    def _on_event(self, event: str) -> None:
        print(f"[EVENT] {event}")

    # ------------------------------------------------------------------ #
    #  Cambio de modelo                                                    #
    # ------------------------------------------------------------------ #

    def _switch_model(self) -> None:
        with self._switch_lock:
            if self._active_model:
                self._active_model.stop()
                time.sleep(0.2)

            self._mode = 1 - self._mode

            if self._mode == 0:
                self._active_model = self._model_a
                print("[CTRL]  Modo → ModelA (autónomo)")
            else:
                self._active_model = self._model_b
                print("[CTRL]  Modo → ModelB (teclado)")

            self._active_model.start()

    def _button_callback(self, channel: int) -> None:
        now = time.time() * 1000
        if now - self._last_btn_time < self.DEBOUNCE_MS:
            return
        self._last_btn_time = now
        # Cambio en thread para no bloquear la ISR de GPIO
        threading.Thread(target=self._switch_model, daemon=True).start()

    # ------------------------------------------------------------------ #
    #  GPIO                                                                #
    # ------------------------------------------------------------------ #

    def _setup_gpio(self) -> None:
        if not _GPIO_AVAILABLE:
            return
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.BUTTON_PIN,
            GPIO.FALLING,
            callback=self._button_callback,
            bouncetime=self.DEBOUNCE_MS,
        )

    def _cleanup_gpio(self) -> None:
        if _GPIO_AVAILABLE:
            GPIO.cleanup()

    # ------------------------------------------------------------------ #
    #  Ciclo de vida                                                       #
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        self._running = True
        self._setup_gpio()
        self._active_model = self._model_a
        self._model_a.start()
        print("[CTRL]  RobotController iniciado.")
        print("[CTRL]  ModelA activo. Presiona GPIO26 para cambiar de modo.")
        print("[CTRL]  Ctrl+C para salir.\n")

    def stop(self) -> None:
        self._running = False
        if self._active_model:
            self._active_model.stop()
        self._cleanup_gpio()
        self._serial.close()
        print("[CTRL]  Sistema detenido.")

    def run(self) -> None:
        """Punto de entrada principal. Bloquea hasta Ctrl+C."""
        self.start()
        try:
            while self._running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


# ------------------------------------------------------------------ #
#  Entry point                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    controller = RobotController()
    controller.run()
