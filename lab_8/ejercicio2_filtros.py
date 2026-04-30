import cv2

class CameraFilters:
    def __init__(self):
        # Iniciar cámara
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.current_filter = 0  # 0 = normal, 1,2,3 filtros

    def apply_filter(self, frame):
        # Filtro 0: normal
        if self.current_filter == 0:
            return frame

        # Filtro 1: escala de grises
        elif self.current_filter == 1:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Filtro 2: bordes
        elif self.current_filter == 2:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.Canny(gray, 100, 200)

        # Filtro 3: blur
        elif self.current_filter == 3:
            return cv2.GaussianBlur(frame, (15, 15), 0)

    def run(self):
        if not self.cap.isOpened():
            print("Error al abrir la cámara")
            return

        while True:
            ret, frame = self.cap.read()

            if not ret:
                print("Error al capturar frame")
                continue

            # Aplicar filtro seleccionado
            processed = self.apply_filter(frame)

            # Mostrar resultado
            cv2.imshow("Camara con Filtros", processed)

            # Leer teclado
            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                break
            elif key == ord('1'):
                self.current_filter = 1
            elif key == ord('2'):
                self.current_filter = 2
            elif key == ord('3'):
                self.current_filter = 3
            elif key == ord('0'):
                self.current_filter = 0

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    app = CameraFilters()
    app.run()
