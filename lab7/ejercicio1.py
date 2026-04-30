import cv2
import sys

def resize_img(img, width, height):
    return cv2.resize(img, (width, height))

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "assets/img1.jpg"
    img = cv2.imread(path)
    if img is None:
        print(f"No se pudo cargar la imagen: {path}")
        sys.exit(1)

    rimg = resize_img(img, 1000, 1000)
    cv2.imshow("1000x1000", rimg)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
