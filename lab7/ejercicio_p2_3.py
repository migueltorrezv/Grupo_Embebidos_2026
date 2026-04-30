import cv2
import sys

"""
HSV = Hue, Saturation, Value
- Hue (matiz): color puro, 0-179 en OpenCV (0=rojo, 60=verde, 120=azul)
- Saturation (saturación): intensidad del color, 0=gris, 255=color puro
- Value (brillo): luminosidad, 0=negro, 255=máximo brillo

HSV es más útil que BGR para detección de colores porque separa
la información de color (hue) de la iluminación (value).
"""

class ImageColorConverter:
    def __init__(self, path: str):
        self._original = cv2.imread(path)
        if self._original is None:
            raise FileNotFoundError(f"No se pudo cargar: {path}")

    def to_rgb(self):
        return cv2.cvtColor(self._original, cv2.COLOR_BGR2RGB)

    def to_hsv(self):
        return cv2.cvtColor(self._original, cv2.COLOR_BGR2HSV)

    def to_grayscale(self):
        return cv2.cvtColor(self._original, cv2.COLOR_BGR2GRAY)

    def show_all(self):
        cv2.imshow("Original (BGR)", self._original)
        # RGB se muestra igual visualmente si se pasa a imshow ya que imshow espera BGR;
        # lo convertimos de vuelta para mostrar correctamente
        rgb = self.to_rgb()
        cv2.imshow("RGB", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        cv2.imshow("HSV", self.to_hsv())
        cv2.imshow("Grayscale", self.to_grayscale())
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/img1.jpg"
    converter = ImageColorConverter(path)
    converter.show_all()
