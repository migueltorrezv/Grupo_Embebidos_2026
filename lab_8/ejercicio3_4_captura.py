import cv2
import os

class CaptureProcessor:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        self.count = 1

        # Carpeta de guardado
        self.save_path = "Captures"
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

    def capture_frames(self):
        if not self.cap.isOpened():
            print("Error al abrir la cámara")
            return None

        last_frame = None

        while True:
            ret, frame = self.cap.read()

            if not ret:
                print("Error al capturar frame")
                continue

            last_frame = frame.copy()

            # Mostrar cámara
            cv2.imshow("Camara (presiona 'f' para capturar)", frame)

            key = cv2.waitKey(1) & 0xFF

            # 🔹 Presionar 'f' para guardar imagen
            if key == ord('f'):
                filename = f"{self.save_path}/image{self.count}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Guardado: {filename}")
                self.count += 1

            # 🔹 ESC para salir
            elif key == 27:
                break

        self.cap.release()
        cv2.destroyAllWindows()

        return last_frame

    def process_image(self, image):
        if image is None:
            print("No hay imagen para procesar")
            return

        # 🔹 Escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 🔹 Dividir en cuadrantes
        h, w = gray.shape

        q1 = gray[:h//2, :w//2]
        q2 = gray[:h//2, w//2:]
        q3 = gray[h//2:, :w//2]
        q4 = gray[h//2:, w//2:]

        # Mostrar resultados
        cv2.imshow("Grayscale", gray)
        cv2.imshow("Cuadrante 1", q1)
        cv2.imshow("Cuadrante 2", q2)
        cv2.imshow("Cuadrante 3", q3)
        cv2.imshow("Cuadrante 4", q4)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def run(self):
        last_frame = self.capture_frames()
        self.process_image(last_frame)


if __name__ == "__main__":
    app = CaptureProcessor()
    app.run()
