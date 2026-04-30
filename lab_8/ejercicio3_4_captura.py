"""
LABORATORIO 8 - Ejercicios 3 y 4
Ejercicio 3: Captura webcam, guarda frames continuamente como "Captures/image1.jpg".
             Al terminar, aplica escala de grises y divide en cuadrantes. OOP.
Ejercicio 4: Modificación: captura frame SOLO cuando se presiona la tecla 'f'.

Controles:
  f -> Capturar frame (Ejercicio 4)
  q -> Salir y procesar última imagen capturada

Uso:
  Ejercicio 3: python ejercicio3_4_captura.py --mode continuous
  Ejercicio 4: python ejercicio3_4_captura.py --mode keypress
"""

import cv2
import numpy as np
import os
import sys


class WebcamCapture:
    """Clase para captura de webcam con guardado de frames."""

    SAVE_DIR = "Captures"
    FILENAME = "image1.jpg"

    def __init__(self, mode="continuous"):
        """
        mode: 'continuous' -> Ejercicio 3 (guarda cada frame)
              'keypress'   -> Ejercicio 4 (guarda al presionar 'f')
        """
        self.mode = mode
        self.cap = None
        self.last_saved_path = None
        os.makedirs(self.SAVE_DIR, exist_ok=True)

    def _save_frame(self, frame):
        path = os.path.join(self.SAVE_DIR, self.FILENAME)
        cv2.imwrite(path, frame)
        self.last_saved_path = path
        print(f"Frame guardado: {path}")

    def _process_final_image(self):
        """Al terminar: aplica grayscale y divide en 4 cuadrantes."""
        if self.last_saved_path is None or not os.path.exists(self.last_saved_path):
            print("No hay imagen guardada para procesar.")
            return

        img = cv2.imread(self.last_saved_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        h, w = gray.shape
        mh, mw = h // 2, w // 2

        q1 = gray[:mh, :mw]   # Top-left
        q2 = gray[:mh, mw:]   # Top-right
        q3 = gray[mh:, :mw]   # Bottom-left
        q4 = gray[mh:, mw:]   # Bottom-right

        top = np.hstack((q1, q2))
        bottom = np.hstack((q3, q4))
        result = np.vstack((top, bottom))

        # Dibujar líneas divisorias
        result_bgr = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        cv2.line(result_bgr, (mw, 0), (mw, h), (0, 255, 0), 2)
        cv2.line(result_bgr, (0, mh), (w, mh), (0, 255, 0), 2)

        # Etiquetas de cuadrantes
        for text, pos in [("Q1", (10, 30)), ("Q2", (mw + 10, 30)),
                           ("Q3", (10, mh + 30)), ("Q4", (mw + 10, mh + 30))]:
            cv2.putText(result_bgr, text, pos, cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 255, 0), 2)

        cv2.imshow('Imagen Final - Grayscale Cuadrantes', result_bgr)
        output_path = os.path.join(self.SAVE_DIR, "image1_processed.jpg")
        cv2.imwrite(output_path, result_bgr)
        print(f"Imagen procesada guardada: {output_path}")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: No se puede abrir la cámara.")
            return

        mode_label = "Continuo (cada frame)" if self.mode == "continuous" else "Tecla 'f'"
        print(f"Modo: {mode_label}")
        print("Presiona 'q' para salir y procesar imagen.")
        if self.mode == "keypress":
            print("Presiona 'f' para capturar frame.")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            display = frame.copy()

            # HUD
            hint = "q:Salir" if self.mode == "continuous" else "f:Capturar | q:Salir"
            cv2.putText(display, hint, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            cv2.imshow('Webcam Capture', display)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif self.mode == "continuous":
                self._save_frame(frame)
            elif self.mode == "keypress" and key == ord('f'):
                self._save_frame(frame)

        self.cap.release()
        cv2.destroyAllWindows()

        self._process_final_image()


def main():
    mode = "continuous"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]

    if mode not in ("continuous", "keypress"):
        print("Error: --mode debe ser 'continuous' o 'keypress'")
        sys.exit(1)

    app = WebcamCapture(mode=mode)
    app.run()


if __name__ == '__main__':
    main()
