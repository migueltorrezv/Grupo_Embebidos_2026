# Lab 7 - Computer Vision con OpenCV
## Raspberry Pi 4 + Cámara USB

### Instalación
```bash
pip install opencv-python numpy
```

### Estructura del proyecto
```
lab7/
├── assets/
│   └── img1.jpg          ← pon tu imagen aquí
├── colors/
│   ├── rojo.jpg
│   ├── verde.jpg
│   └── azul.jpg
├── Captures/             ← se crea automáticamente
├── ejercicio1.py
├── ejercicio2.py
├── ejercicio3.py
├── ejercicio4.py
├── ejercicio_p2_1.py
├── ejercicio_p2_2.py
├── ejercicio_p2_3.py
├── ejercicio_p2_4.py
├── ejercicio_p2_5.py
└── ejercicio_p2_6.py
```

### Ejecución
```bash
# Parte 1
python ejercicio1.py assets/img1.jpg
python ejercicio2.py assets/img1.jpg
python ejercicio3.py assets/img1.jpg
python ejercicio4.py assets/img1.jpg

# Parte 2
python ejercicio_p2_1.py           # requiere carpeta colors/
python ejercicio_p2_2.py assets/img1.jpg
python ejercicio_p2_3.py assets/img1.jpg
python ejercicio_p2_4.py assets/img1.jpg
python ejercicio_p2_5.py           # requiere cámara USB en /dev/video0
python ejercicio_p2_6.py           # requiere cámara USB en /dev/video0
```

### Notas para Raspberry Pi 4
- Si `imshow` falla sin entorno gráfico, ejecutar con: `DISPLAY=:0 python ejercicioX.py`
- Cámara USB: verificar con `ls /dev/video*`
- Si hay múltiples cámaras, cambiar `VideoCapture(0)` → `VideoCapture(1)`
- Para enviar datos a TIVA por UART: `pip install pyserial`

### Controles de teclado (ejercicios con webcam)
| Tecla | Acción |
|-------|--------|
| G | Modo grayscale |
| R | Modo RGB |
| C | Capturar frame |
| ESC | Salir |
