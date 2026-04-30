import cv2

def main():
    # 🔹 Cargar video (pon tu ruta aquí)
    cap = cv2.VideoCapture("video.mp4")

    if not cap.isOpened():
        print("Error: no se pudo abrir el video")
        return

    while True:
        ret, frame = cap.read()

        # 🔧 Si el video termina, vuelve al inicio
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # 🔹 1. Redimensionar a 400x600
        resized = cv2.resize(frame, (400, 600))

        # 🔹 2. Detector de bordes
        edges = cv2.Canny(resized, 100, 200)

        # 🔹 3. Mitades
        h, w, _ = resized.shape
        left_half = resized[:, :w//2]
        right_half = resized[:, w//2:]

        # 🔹 4. Cuadrantes
        top_left = resized[:h//2, :w//2]
        top_right = resized[:h//2, w//2:]
        bottom_left = resized[h//2:, :w//2]
        bottom_right = resized[h//2:, w//2:]

        # 🔹 Mostrar ventanas
        cv2.imshow("Video Redimensionado", resized)
        cv2.imshow("Bordes", edges)
        cv2.imshow("Mitad Izquierda", left_half)
        cv2.imshow("Mitad Derecha", right_half)
        cv2.imshow("Cuadrante 1", top_left)
        cv2.imshow("Cuadrante 2", top_right)
        cv2.imshow("Cuadrante 3", bottom_left)
        cv2.imshow("Cuadrante 4", bottom_right)

        # 🔹 ESC para salir
        if cv2.waitKey(25) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
