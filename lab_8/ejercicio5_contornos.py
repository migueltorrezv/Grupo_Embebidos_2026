import cv2
import sys

def main():
    # 🔹 Verificar si pasas imagen por terminal
    if len(sys.argv) > 1:
        path = sys.argv[1]
        image = cv2.imread(path)

        if image is None:
            print(f"Error: no se pudo cargar {path}")
            return
    else:
        print("No se pasó imagen, usando imagen por defecto")
        image = cv2.imread("imagen.jpg")

        if image is None:
            print("Error: no existe 'imagen.jpg'")
            return

    # 🔹 Redimensionar (más cómodo)
    image = cv2.resize(image, (600, 500))

    # 🔹 Escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 🔹 Blur (mejora detección)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 🔹 Threshold
    _, thresh = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY)

    # 🔹 Contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 🔹 Dibujar contornos
    output = image.copy()
    cv2.drawContours(output, contours, -1, (0, 255, 0), 2)

    # 🔹 Mostrar número de contornos en pantalla
    cv2.putText(output, f"Contornos: {len(contours)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # 🔹 Mostrar ventanas
    cv2.imshow("Original", image)
    cv2.imshow("Threshold", thresh)
    cv2.imshow("Contornos", output)

    print(f"Contornos detectados: {len(contours)}")

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
