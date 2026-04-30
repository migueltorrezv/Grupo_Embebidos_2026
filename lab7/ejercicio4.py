import cv2
import sys

def show_and_wait(title, img):
    cv2.imshow(title, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/img1.jpg"
    img = cv2.imread(path)
    if img is None:
        print(f"No se pudo cargar la imagen: {path}")
        sys.exit(1)

    # 1. Mostrar original
    show_and_wait("Original", img)

    # 2. Resize a 400x600 (width=400, height=600)
    img = cv2.resize(img, (400, 600))
    show_and_wait("Resize 400x600", img)

    h, w = img.shape[:2]  # h=600, w=400

    # 3. Corte horizontal — mitad superior y mitad inferior
    top    = img[:h//2, :]
    bottom = img[h//2:, :]
    show_and_wait("Top half", top)
    show_and_wait("Bottom half", bottom)

    # 4. Corte vertical — mitad izquierda y mitad derecha
    left  = img[:, :w//2]
    right = img[:, w//2:]
    show_and_wait("Left half", left)
    show_and_wait("Right half", right)

    # 5. Cuadrantes
    quadrants = [
        img[:h//2, :w//2],   # Q1 - superior izquierdo
        img[:h//2, w//2:],   # Q2 - superior derecho
        img[h//2:, :w//2],   # Q3 - inferior izquierdo
        img[h//2:, w//2:],   # Q4 - inferior derecho
    ]
    for i, q in enumerate(quadrants, 1):
        show_and_wait(f"Quadrant {i}", q)
