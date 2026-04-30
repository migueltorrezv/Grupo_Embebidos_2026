import cv2

"""
Raspberry Pi 4 + cámara USB:
- cv2.VideoCapture(0) abre /dev/video0 (primera cámara USB)
- Si falla, probar VideoCapture(1) o VideoCapture(2)

Controles:
  G  →  Grayscale
  R  →  RGB (BGR en OpenCV)
  ESC → Salir
"""

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara. Verifica /dev/video0")
        return

    mode = "rgb"
    print("Cámara abierta. Teclas: G=grayscale | R=RGB | ESC=salir")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error leyendo frame.")
            break

        if mode == "gray":
            display = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            title = "Grayscale"
        else:
            display = frame
            title = "RGB (BGR)"

        cv2.imshow(title, display)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:       # ESC
            break
        elif key == ord('g') or key == ord('G'):
            mode = "gray"
            cv2.destroyAllWindows()
        elif key == ord('r') or key == ord('R'):
            mode = "rgb"
            cv2.destroyAllWindows()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
