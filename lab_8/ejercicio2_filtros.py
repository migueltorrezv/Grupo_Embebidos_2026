"""
LABORATORIO 8 - Ejercicio 2
Cámara con 3 filtros seleccionables usando OOP.

Controles:
  1 -> Filtro Escala de Grises
  2 -> Filtro Canny (bordes)
  3 -> Filtro HSV
  q -> Salir
"""

import cv2
import numpy as np


class Filter:
    """Clase base para filtros de imagen."""
    def apply(self, frame):
        raise NotImplementedError

    @property
    def name(self):
        raise NotImplementedError


class GrayscaleFilter(Filter):
    @property
    def name(self):
        return "Escala de Grises"

    def apply(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # Convertir de vuelta para imshow uniforme


class CannyFilter(Filter):
    def __init__(self, threshold1=100, threshold2=200):
        self.threshold1 = threshold1
        self.threshold2 = threshold2

    @property
    def name(self):
        return "Detección de Bordes (Canny)"

    def apply(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, self.threshold1, self.threshold2)
        return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)


class HSVFilter(Filter):
    @property
    def name(self):
        return "Espacio de Color HSV"

    def apply(self, frame):
        return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


class CameraApp:
    """Aplicación principal de cámara con filtros seleccionables."""

    def __init__(self):
        self.filters = {
            ord('1'): GrayscaleFilter(),
            ord('2'): CannyFilter(),
            ord('3'): HSVFilter(),
        }
        self.active_filter = None
        self.cap = None

    def _draw_overlay(self, frame):
        """Dibuja HUD con filtro activo y controles."""
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - 80), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        filter_name = self.active_filter.name if self.active_filter else "Sin filtro"
        cv2.putText(frame, f"Filtro: {filter_name}", (10, h - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "1:Gris | 2:Canny | 3:HSV | q:Salir", (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        return frame

    def run(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: No se puede abrir la cámara.")
            return

        print("Cámara iniciada. Presiona 1, 2 o 3 para seleccionar filtro. 'q' para salir.")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            display = frame.copy()

            if self.active_filter:
                display = self.active_filter.apply(display)

            display = self._draw_overlay(display)
            cv2.imshow('Camara con Filtros', display)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key in self.filters:
                self.active_filter = self.filters[key]
                print(f"Filtro activo: {self.active_filter.name}")

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    app = CameraApp()
    app.run()
