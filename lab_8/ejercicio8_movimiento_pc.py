"""
LABORATORIO 8 - Ejercicio 8
Sistema de dos partes:
  A) [PC/Raspberry Pi] Detección de movimiento con background subtraction.
     Envía señal por UART serial al Pico 2W cuando detecta movimiento.

  B) [Pico 2W] Recibe señal UART y activa buzzer como alarma.

--- PARTE A: Correr en PC o Raspberry Pi ---
Dependencias: opencv-python, pyserial
Instalar: pip install opencv-python pyserial

Puerto serial del Pico 2W:
  Linux: /dev/ttyACM0
  Windows: COM3 (ajustar según Device Manager)
"""

# ============================================================
# PARTE A - PC / Raspberry Pi (Python 3 + OpenCV)
# ============================================================

import cv2
import numpy as np
import serial
import time
import sys

# Ajustar puerto según sistema operativo
SERIAL_PORT = '/dev/ttyACM0'  # Linux/RPi
BAUD_RATE   = 9600


class MotionDetector:
    """Detección de movimiento con background subtraction MOG2."""

    MIN_AREA = 1500  # Área mínima para considerar movimiento real (filtro de ruido)

    def __init__(self, camera_index=0, serial_port=None):
        self.cap = cv2.VideoCapture(camera_index)
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=50, detectShadows=False
        )
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.motion_detected = False
        self.serial_conn = None

        # Intentar conectar serial (opcional, no obligatorio)
        if serial_port:
            try:
                self.serial_conn = serial.Serial(serial_port, BAUD_RATE, timeout=1)
                time.sleep(2)  # Esperar inicialización del Pico
                print(f"Serial conectado en {serial_port}")
            except Exception as e:
                print(f"Advertencia: No se pudo conectar serial: {e}")
                print("Continuando sin comunicación serial.")

    def _send_signal(self, motion: bool):
        """Envía '1' (movimiento) o '0' (sin movimiento) al Pico 2W."""
        if self.serial_conn and self.serial_conn.is_open:
            byte = b'1' if motion else b'0'
            self.serial_conn.write(byte)

    def _process_frame(self, frame):
        frame = cv2.resize(frame, (640, 480))

        # 1. Background subtraction -> máscara de foreground
        fg_mask = self.bg_subtractor.apply(frame)

        # 2. Operaciones morfológicas para limpiar ruido
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)   # Erosión + Dilatación
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)  # Dilatación + Erosión
        fg_mask = cv2.dilate(fg_mask, self.kernel, iterations=2)

        # 3. findContours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant = [c for c in contours if cv2.contourArea(c) > self.MIN_AREA]

        motion = len(significant) > 0

        # 4. drawContours + HUD
        result = frame.copy()
        cv2.drawContours(result, significant, -1, (0, 255, 0), 2)

        if motion:
            cv2.putText(result, "¡MOVIMIENTO DETECTADO!", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        status_color = (0, 0, 255) if motion else (0, 255, 0)
        cv2.putText(result, f"Objetos: {len(significant)}", (10, 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        cv2.putText(result, "q: Salir", (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return result, fg_mask, motion

    def run(self):
        if not self.cap.isOpened():
            print("Error: No se puede abrir la cámara.")
            return

        print("Detector de movimiento iniciado. Presiona 'q' para salir.")
        prev_motion = False

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            result, mask, motion = self._process_frame(frame)

            # Enviar señal solo cuando cambia el estado
            if motion != prev_motion:
                self._send_signal(motion)
                prev_motion = motion
                print(f"Estado: {'Movimiento' if motion else 'Sin movimiento'}")

            cv2.imshow('Detector de Movimiento', result)
            cv2.imshow('Foreground Mask', mask)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

        self._send_signal(False)  # Apagar alarma al salir
        self.cap.release()
        if self.serial_conn:
            self.serial_conn.close()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    port = sys.argv[1] if len(sys.argv) > 1 else SERIAL_PORT
    detector = MotionDetector(camera_index=0, serial_port=port)
    detector.run()
