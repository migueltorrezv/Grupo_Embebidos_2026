import cv2
import os

"""
Raspberry Pi 4 + cámara USB:
- Guarda frames en Captures/image1.jpg cada vez que se presiona 'C'
- Al terminar (ESC), aplica grayscale y divide en cuadrantes la ÚLTIMA imagen capturada

Controles:
  C   → Capturar y guardar frame
  ESC → Terminar, procesar última captura
"""

SAVE_DIR  = "Captures"
SAVE_PATH = os.path.join(SAVE_DIR, "image1.jpg")

def process_last_capture(path):
    img = cv2.imread(path)
    if img is None:
        print("No hay capturas guardadas.")
        return

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow("Captura - Grayscale", gray)

    # Cuadrantes
    h, w = img.shape[:2]
    quadrants = {
        "Quadrant 1": img[:h//2, :w//2],
        "Quadrant 2": img[:h//2, w//2:],
        "Quadrant 3": img[h//2:, :w//2],
        "Quadrant 4": img[h//2:, w//2:],
    }
    for title, q in quadrants.items():
        cv2.imshow(title, q)

    print("Presiona cualquier tecla para cerrar.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    print("Cámara abierta. Teclas: C=capturar | ESC=salir")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error leyendo frame.")
            break

        cv2.imshow("Webcam - presiona C para capturar", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            break
        elif key == ord('c') or key == ord('C'):
            cv2.imwrite(SAVE_PATH, frame)
            print(f"Frame guardado: {SAVE_PATH}")

    cap.release()
    cv2.destroyAllWindows()

    # Procesar última captura
    if os.path.exists(SAVE_PATH):
        process_last_capture(SAVE_PATH)
    else:
        print("No se capturó ninguna imagen.")

if __name__ == "__main__":
    main()
