import cv2
import sys

"""
Diferencia entre print e imshow:
- print: imprime la matriz NumPy en terminal (texto), no muestra imagen visual.
- imshow: abre ventana GUI y renderiza la imagen. Requiere entorno gráfico (display).
  En Raspberry Pi sin escritorio, imshow falla. Usar VNC o ejecutar con DISPLAY configurado.
"""

ROTATIONS = [
    cv2.ROTATE_90_CLOCKWISE,
    cv2.ROTATE_180,
    cv2.ROTATE_90_COUNTERCLOCKWISE,
]

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/img1.jpg"
    img = cv2.imread(path)
    if img is None:
        print(f"No se pudo cargar la imagen: {path}")
        sys.exit(1)

    angle = 0
    print("Presiona cualquier tecla para rotar 90°. ESC para salir.")

    while True:
        if angle % 4 == 0:
            display = img.copy()
        else:
            display = cv2.rotate(img, ROTATIONS[(angle - 1) % 3])

        cv2.imshow(f"Rotación {(angle * 90) % 360}°", display)
        key = cv2.waitKey(0)

        if key == 27:  # ESC
            break
        angle += 1
        cv2.destroyAllWindows()

    cv2.destroyAllWindows()
