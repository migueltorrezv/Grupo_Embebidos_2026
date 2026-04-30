"""
LABORATORIO 8 - Ejercicio 9
Extensión del ejercicio 8:
  - Dibuja contorno del objeto detectado
  - Muestra número de objetos encontrados
  - Si objetos > 1  -> envía '2' al Pico (todos los LEDs encendidos)
  - Si objetos == 1 -> envía '1' al Pico (2 LEDs encendidos)
  - Si objetos == 0 -> envía '0' al Pico (todos LEDs apagados)

Parte A: PC/Raspberry Pi (este archivo)
Parte B: Pico 2W -> ver ejercicio9_leds_pico2w.py
"""

import cv2
import numpy as np
import serial
import time
import sys

SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE   = 9600


class ObjectCountDetector:
    MIN_AREA = 1500

    def __init__(self, camera_index=0, serial_port=None):
        self.cap = cv2.VideoCapture(camera_index)
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=False
        )
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.serial_conn = None
        self.prev_state = -1  # -1 = desconocido

        if serial_port:
            try:
                self.serial_conn = serial.Serial(serial_port, BAUD_RATE, timeout=1)
                time.sleep(2)
                print(f"Serial conectado en {serial_port}")
            except Exception as e:
                print(f"Advertencia: serial no disponible: {e}")

    def _send_state(self, state: int):
        """state: 0=ninguno, 1=un objeto, 2=más de uno"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.write(str(state).encode())

    def _process_frame(self, frame):
        frame = cv2.resize(frame, (640, 480))

        fg_mask = self.bg_subtractor.apply(frame)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        fg_mask = cv2.dilate(fg_mask, self.kernel, iterations=2)

        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant = [c for c in contours if cv2.contourArea(c) > self.MIN_AREA]
        count = len(significant)

        result = frame.copy()

        # drawContours con bounding boxes y etiquetas
        for i, contour in enumerate(significant):
            cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result, (x, y), (x + w, y + h), (255, 0, 0), 1)
            cv2.putText(result, f"Obj {i+1}", (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # HUD
        if count > 1:
            msg = f"Objetos: {count} -> TODOS LOS LEDs ON"
            color = (0, 0, 255)
        elif count == 1:
            msg = "Objetos: 1 -> 2 LEDs ON"
            color = (0, 165, 255)
        else:
            msg = "Sin objetos detectados"
            color = (0, 255, 0)

        cv2.putText(result, msg, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(result, "q: Salir", (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

        return result, fg_mask, count

    def run(self):
        if not self.cap.isOpened():
            print("Error: No se puede abrir la cámara.")
            return

        print("Detector de objetos iniciado. Presiona 'q' para salir.")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            result, mask, count = self._process_frame(frame)

            # Determinar estado
            if count > 1:
                state = 2
            elif count == 1:
                state = 1
            else:
                state = 0

            # Enviar solo si cambia
            if state != self.prev_state:
                self._send_state(state)
                self.prev_state = state
                print(f"Objetos: {count} | Estado enviado: {state}")

            cv2.imshow('Detector de Objetos', result)
            cv2.imshow('Foreground Mask', mask)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        self._send_state(0)
        self.cap.release()
        if self.serial_conn:
            self.serial_conn.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else SERIAL_PORT
    detector = ObjectCountDetector(camera_index=0, serial_port=port)
    detector.run()
