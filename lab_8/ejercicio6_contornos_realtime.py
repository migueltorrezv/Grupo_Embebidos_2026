import cv2

def main():
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("Error al abrir la cámara")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error al capturar frame")
            continue

        # 🔹 Redimensionar (más ligero)
        frame = cv2.resize(frame, (640, 480))

        # 🔹 Escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 🔹 Suavizado
        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        # 🔹 Detección de bordes
        edges = cv2.Canny(blur, 100, 200)

        # 🔹 Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 🔹 Dibujar contornos
        output = frame.copy()
        cv2.drawContours(output, contours, -1, (0, 255, 0), 2)

        # 🔹 Mostrar
        cv2.imshow("Original", frame)
        cv2.imshow("Contornos en tiempo real", output)

        # 🔹 Salir con ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
