import cv2
import numpy as np
import os

"""
Estructura esperada:
colors/
  rojo.jpg
  verde.jpg
  azul.jpg

El script lee cada imagen y calcula el valor promedio de color en BGR y RGB.
"""

COLOR_DIR = "colors"

def get_avg_color(img):
    avg_bgr = img.mean(axis=(0, 1))  # promedio por canal
    avg_rgb = avg_bgr[::-1]
    return avg_bgr, avg_rgb

if __name__ == "__main__":
    if not os.path.isdir(COLOR_DIR):
        print(f"Carpeta '{COLOR_DIR}' no encontrada.")
        raise SystemExit(1)

    images = [f for f in os.listdir(COLOR_DIR)
              if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    if not images:
        print("No hay imágenes en la carpeta 'colors'.")
        raise SystemExit(1)

    for fname in images:
        path = os.path.join(COLOR_DIR, fname)
        img = cv2.imread(path)
        if img is None:
            print(f"No se pudo cargar: {fname}")
            continue

        avg_bgr, avg_rgb = get_avg_color(img.astype(np.float32))
        print(f"\n{fname}")
        print(f"  BGR promedio : B={avg_bgr[0]:.1f}  G={avg_bgr[1]:.1f}  R={avg_bgr[2]:.1f}")
        print(f"  RGB promedio : R={avg_rgb[0]:.1f}  G={avg_rgb[1]:.1f}  B={avg_rgb[2]:.1f}")

        cv2.imshow(fname, img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
