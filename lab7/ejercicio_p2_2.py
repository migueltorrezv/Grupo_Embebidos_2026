import cv2
import numpy as np
import sys

"""
Fórmula estándar ITU-R BT.601:
  Gray = 0.299*R + 0.587*G + 0.114*B

OpenCV carga en BGR, por eso el orden es B=img[:,:,0], G=img[:,:,1], R=img[:,:,2]
"""

def rgb_to_grayscale(img_bgr):
    """Convierte imagen BGR a escala de grises manualmente (sin cv2.cvtColor)."""
    B = img_bgr[:, :, 0].astype(np.float32)
    G = img_bgr[:, :, 1].astype(np.float32)
    R = img_bgr[:, :, 2].astype(np.float32)
    gray = (0.299 * R + 0.587 * G + 0.114 * B).astype(np.uint8)
    return gray

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/img1.jpg"
    img = cv2.imread(path)
    if img is None:
        print(f"No se pudo cargar: {path}")
        raise SystemExit(1)

    gray_manual = rgb_to_grayscale(img)
    gray_cv2    = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.imshow("Original BGR", img)
    cv2.imshow("Grayscale Manual", gray_manual)
    cv2.imshow("Grayscale cv2 (referencia)", gray_cv2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
