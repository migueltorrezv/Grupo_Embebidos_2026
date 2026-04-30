import cv2
import sys

SIZES = {
    "1": ("original", None),
    "2": ("small",    (320, 240)),
    "3": ("medium",   (640, 480)),
    "4": ("big",      (1280, 720)),
}

def resize_img(img, dims):
    if dims is None:
        return img
    return cv2.resize(img, dims)

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/img1.jpg"
    img = cv2.imread(path)
    if img is None:
        print(f"No se pudo cargar la imagen: {path}")
        sys.exit(1)

    print("Selecciona el tamaño:")
    for key, (name, dims) in SIZES.items():
        label = f"{dims[0]}x{dims[1]}" if dims else "original"
        print(f"  {key}. {name} ({label})")

    choice = input("Opción: ").strip()
    if choice not in SIZES:
        print("Opción inválida.")
        sys.exit(1)

    name, dims = SIZES[choice]
    rimg = resize_img(img, dims)
    h, w = rimg.shape[:2]
    cv2.imshow(f"{name} - {w}x{h}", rimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
