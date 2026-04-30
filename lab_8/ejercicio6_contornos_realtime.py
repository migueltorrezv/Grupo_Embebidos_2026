"""
LABORATORIO 8 - Ejercicio 6
Detección de contornos en tiempo real con webcam.
Compatible con laptop y Raspberry Pi.

Diferencia en Raspberry Pi:
- FPS más bajo debido a menor poder de procesamiento
- Recomendable reducir resolución (ya incluido: 320x240)
- Usar cv2.CHAIN_APPROX_SIMPLE para menor uso de memoria

Presiona 'q' para salir.
"""

import cv2
import numpy as np
import time


class RealTimeContourDetector:
    def __init__(self, camera_index=0, width=320, height=240):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self.fps = 0
        self._prev_time = 0

    def _calculate_fps(self):
        current_time = time.time()
        self.fps = 1 / (current_time - self._prev_time) if self._prev_time else 0
        self._prev_time = current_time

    def _process_frame(self, frame):
        # Redimensionar para mejor rendimiento en Raspberry Pi
        frame = cv2.resize(frame, (self.width, self.height))

        # Grayscale + blur para reducir ruido
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)

        # findContours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filtrar contornos pequeños (ruido)
        significant = [c for c in contours if cv2.contourArea(c) > 300]

        # drawContours sobre frame original
        result = frame.copy()
        cv2.drawContours(result, significant, -1, (0, 255, 0), 2)

        # HUD
        cv2.putText(result, f"FPS: {self.fps:.1f}", (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(result, f"Contornos: {len(significant)}", (5, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        cv2.putText(result, "q: Salir", (5, self.height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        return result, edges

    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: No se puede abrir la cámara {self.camera_index}")
            return

        # Configurar resolución
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        print("Detección de contornos en tiempo real.")
        print("Presiona 'q' para salir.")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error al leer frame.")
                break

            self._calculate_fps()
            result, edges = self._process_frame(frame)

            cv2.imshow('Contornos en Tiempo Real', result)
            cv2.imshow('Edges (Canny)', edges)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    # En Raspberry Pi usar resolución más baja si hay lag: width=240, height=180
    detector = RealTimeContourDetector(camera_index=0, width=320, height=240)
    detector.run()
