import threading
import time

try:
    from pynput import keyboard as pynput_keyboard
    _PYNPUT_AVAILABLE = True
except ImportError:
    _PYNPUT_AVAILABLE = False

try:
    import readchar
    _READCHAR_AVAILABLE = True
except ImportError:
    _READCHAR_AVAILABLE = False


class ModelA:
    """
    Control por teclado SSH.
      W → forward   S → backward   A → left   D → right
      N → nitro (1ª vez = 100 % PWM, 2ª vez = 70 %)
      Espacio → stop
    Stop automático si dist <= 5 cm.
    """

    OBSTACLE_DIST_CM = 5
    NITRO_SPEED      = 100
    NORMAL_SPEED     = 70

    # Mapa tecla → comando UART
    _KEY_MAP = {
        'w': "forward",
        's': "backward",
        'a': "left",
        'd': "right",
    }

    def __init__(self, serial_conn):
        self._serial   = serial_conn
        self._running  = False
        self._dist     = 999
        self._blocked  = False
        self._nitro_on = False
        self._lock     = threading.Lock()

        # Callbacks (punteros a función)
        self.on_distance: callable = None
        self.on_event:    callable = None

        self._serial_thread:   threading.Thread = None
        self._keyboard_thread: threading.Thread = None
        self._listener = None  # pynput Listener

    # ------------------------------------------------------------------ #
    #  API pública                                                         #
    # ------------------------------------------------------------------ #

    def start(self) -> None:
        if self._running:
            return
        self._running = True

        self._serial_thread = threading.Thread(target=self._read_serial, daemon=True)
        self._serial_thread.start()

        if _PYNPUT_AVAILABLE:
            self._start_pynput()
        elif _READCHAR_AVAILABLE:
            self._keyboard_thread = threading.Thread(target=self._readchar_loop, daemon=True)
            self._keyboard_thread.start()
        else:
            raise RuntimeError("Instala pynput o readchar: pip install pynput readchar")

    def stop(self) -> None:
        self._running = False
        self._send("stop")
        if self._listener:
            self._listener.stop()

    # ------------------------------------------------------------------ #
    #  Internos – serial                                                   #
    # ------------------------------------------------------------------ #

    def _send(self, command: str) -> None:
        with self._lock:
            self._serial.write(f"{command}\n".encode())

    def _read_serial(self) -> None:
        while self._running:
            try:
                if self._serial.in_waiting:
                    msg = self._serial.readline().decode().strip()
                    if msg.startswith("dist:"):
                        raw = msg.split(":")[1]
                        dist = int(raw) if raw.isdigit() else 999
                        self._dist = dist
                        if self.on_distance:
                            self.on_distance(dist)
                        self._check_obstacle(dist)
                    else:
                        if self.on_event:
                            self.on_event(msg)
            except Exception:
                pass
            time.sleep(0.05)

    def _check_obstacle(self, dist: int) -> None:
        if dist != 999 and dist <= self.OBSTACLE_DIST_CM:
            if not self._blocked:
                self._blocked = True
                self._send("stop")
                if self.on_event:
                    self.on_event(f"auto_stop:{dist}cm")
        elif dist == 999 or dist > self.OBSTACLE_DIST_CM:
            self._blocked = False   # camino libre, desbloquear

    # ------------------------------------------------------------------ #
    #  Internos – lógica de teclas                                         #
    # ------------------------------------------------------------------ #

    def _handle_key(self, char: str) -> None:
        if char in self._KEY_MAP:
            if not self._blocked:
                self._send(self._KEY_MAP[char])
        elif char == 'n':
            self._toggle_nitro()
        elif char == ' ':
            self._send("stop")

    def _toggle_nitro(self) -> None:
        if not self._nitro_on:
            self._nitro_on = True
            self._send(f"speed:{self.NITRO_SPEED}")
            if self.on_event:
                self.on_event("nitro:100%")
        else:
            self._nitro_on = False
            self._send(f"speed:{self.NORMAL_SPEED}")
            if self.on_event:
                self.on_event("nitro:off→70%")

    # ------------------------------------------------------------------ #
    #  Backend pynput                                                      #
    # ------------------------------------------------------------------ #

    def _start_pynput(self) -> None:
        def on_press(key):
            if not self._running:
                return False
            try:
                char = key.char.lower() if hasattr(key, 'char') and key.char else None
            except AttributeError:
                char = None

            if char:
                self._handle_key(char)
            elif key == pynput_keyboard.Key.space:
                self._send("stop")

        def on_release(key):
            if not self._running:
                return False
            try:
                char = key.char.lower() if hasattr(key, 'char') and key.char else None
            except AttributeError:
                char = None
            # Soltar tecla de movimiento → stop
            if char in self._KEY_MAP:
                self._send("stop")

        self._listener = pynput_keyboard.Listener(
            on_press=on_press, on_release=on_release
        )
        self._listener.start()

    # ------------------------------------------------------------------ #
    #  Backend readchar (fallback)                                         #
    # ------------------------------------------------------------------ #

    def _readchar_loop(self) -> None:
        while self._running:
            try:
                ch = readchar.readchar().lower()
                self._handle_key(ch)
            except Exception:
                pass

