"""
LABORATORIO 8 - Ejercicio 1
Video operations with OpenCV
Uso: python ejercicio1_video.py <ruta_video>
"""

import cv2
import numpy as np
import sys

def play_video(cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow('Video Original', frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def resize_video(cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized = cv2.resize(frame, (400, 600))
        cv2.imshow('Video Resized 400x600', resized)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def edge_detector_video(cap):
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized = cv2.resize(frame, (400, 600))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        cv2.imshow('Edge Detector', edges)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def two_halves_video(cap):
    """Divide frame en mitad izquierda y mitad derecha, mostradas lado a lado."""
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized = cv2.resize(frame, (400, 600))
        h, w = resized.shape[:2]
        mid = w // 2
        left = resized[:, :mid]
        right = resized[:, mid:]
        combined = np.hstack((left, right))
        cv2.imshow('Two Halves', combined)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def quadrants_video(cap):
    """Divide frame en 4 cuadrantes y los muestra en una grilla 2x2."""
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized = cv2.resize(frame, (400, 600))
        h, w = resized.shape[:2]
        mh, mw = h // 2, w // 2

        q1 = resized[:mh, :mw]    # Top-left
        q2 = resized[:mh, mw:]    # Top-right
        q3 = resized[mh:, :mw]    # Bottom-left
        q4 = resized[mh:, mw:]    # Bottom-right

        top = np.hstack((q1, q2))
        bottom = np.hstack((q3, q4))
        grid = np.vstack((top, bottom))

        cv2.imshow('Four Quadrants', grid)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()

def main():
    if len(sys.argv) < 2:
        print("Uso: python ejercicio1_video.py <ruta_video>")
        sys.exit(1)

    video_path = sys.argv[1]
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: No se puede abrir el video '{video_path}'")
        sys.exit(1)

    print("Ejecutando operaciones sobre el video...")
    print("Presiona 'q' para pasar a la siguiente operación\n")

    print("1. Video original")
    play_video(cap)

    print("2. Video redimensionado a 400x600")
    resize_video(cap)

    print("3. Detección de bordes (Canny)")
    edge_detector_video(cap)

    print("4. Video dividido en dos mitades")
    two_halves_video(cap)

    print("5. Video dividido en cuadrantes")
    quadrants_video(cap)

    cap.release()
    print("Ejercicio 1 completado.")

if __name__ == '__main__':
    main()
