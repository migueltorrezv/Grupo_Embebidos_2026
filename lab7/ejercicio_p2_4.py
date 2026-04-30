import cv2
import numpy as np
import sys

"""
Detección de colores en HSV y cómo pasar a TIVA:

Los rangos HSV en OpenCV son: H=0-179, S=0-255, V=0-255

TIVA: Los valores detectados (porcentaje de píxeles o presencia True/False)
se pueden enviar por UART desde la Raspberry Pi a la TIVA usando pyserial:
  import serial
  ser = serial.Serial('/dev/ttyUSB0', 9600)
  ser.write(b'R')  # enviar 'R' si se detecta rojo

Para este ejercicio: detección sobre imagen estática.
Para video (webcam), ver ejercicio_p2_5.py
"""

COLOR_RANGES = {
    "rojo": [
        (np.array([0,   120, 70]),  np.array([10,  255, 255])),
        (np.array([170, 120, 70]),  np.array([180, 255, 255])),  # rojo envuelve 0°
    ],
    "verde": [
        (np.array([40,  50,  50]),  np.array([80,  255, 255])),
    ],
    "azul": [
        (np.array([100, 50,  50]),  np.array([130, 255, 255])),
    ],
}

def detect_color(hsv_img, color_name):
    ranges = COLOR_RANGES[color_name]
    mask = np.zeros(hsv_img.shape[:2], dtype=np.uint8)
    for (lower, upper) in ranges:
        mask |= cv2.inRange(hsv_img, lower, upper)
    pixel_count = cv2.countNonZero(mask)
    detected = pixel_count > 500  # umbral mínimo
    return detected, pixel_count, mask

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/img1.jpg"
    img = cv2.imread(path)
    if img is None:
        print(f"No se pudo cargar: {path}")
        raise SystemExit(1)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    for color in ["rojo", "verde", "azul"]:
        detected, count, mask = detect_color(hsv, color)
        print(f"{color.upper():6s} — detectado: {detected} | píxeles: {count}")
        cv2.imshow(f"Máscara {color}", mask)

    print("\n--- TIVA (UART) ---")
    print("Enviar por serial: R=rojo, G=verde, B=azul")
    print("Ejemplo: ser.write(b'R') si rojo detectado")

    cv2.imshow("Original", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
