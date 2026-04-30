"""
LABORATORIO 8 - Ejercicio 5
Detectar contornos de una imagen usando findContours() y drawContours().

Uso: python ejercicio5_contornos.py <ruta_imagen>
     python ejercicio5_contornos.py  (sin args -> genera imagen de prueba)
"""

import cv2
import numpy as np
import sys


def detect_and_draw_contours(image_path=None):
    # Si no se provee imagen, generar imagen de prueba con figuras
    if image_path is None:
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(img, (50, 50), (200, 200), (255, 255, 255), -1)
        cv2.circle(img, (400, 150), 80, (255, 255, 255), -1)
        cv2.ellipse(img, (300, 380), (120, 60), 0, 0, 360, (255, 255, 255), -1)
        print("Usando imagen de prueba generada.")
    else:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: No se puede cargar '{image_path}'")
            sys.exit(1)

    original = img.copy()

    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Aplicar threshold binario para obtener máscara
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    # 3. findContours
    # RETR_EXTERNAL: solo contornos externos
    # CHAIN_APPROX_SIMPLE: comprime segmentos horizontales/verticales/diagonales
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Contornos encontrados: {len(contours)}")

    # 4. drawContours
    result = original.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 2)  # -1 = todos los contornos

    # Añadir info de cada contorno
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(result, f"#{i} A={int(area)}", (cx - 30, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    # Mostrar resultados
    cv2.imshow('Original', original)
    cv2.imshow('Threshold', thresh)
    cv2.imshow('Contornos detectados', result)

    print("Presiona cualquier tecla para salir.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else None
    detect_and_draw_contours(path)
