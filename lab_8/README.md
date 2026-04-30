# LAB 8 - Embedded Computer Vision
## Guía de uso y conexiones

---

## Dependencias Python (PC / Raspberry Pi)
```bash
pip install opencv-python numpy pyserial
```

---

## Ejercicio 1 - Operaciones sobre video
```bash
python ejercicio1_video.py mi_video.mp4
```
- Presiona `q` para pasar a la siguiente operación
- Operaciones: original → resize 400x600 → Canny edges → 2 mitades → 4 cuadrantes

---

## Ejercicio 2 - Cámara con 3 filtros (OOP)
```bash
python ejercicio2_filtros.py
```
| Tecla | Filtro |
|-------|--------|
| `1` | Escala de grises |
| `2` | Canny (bordes) |
| `3` | HSV |
| `q` | Salir |

---

## Ejercicio 3 - Captura continua + cuadrantes (OOP)
```bash
python ejercicio3_4_captura.py --mode continuous
```
- Guarda cada frame en `Captures/image1.jpg` (sobreescribe)
- Al salir con `q`: muestra imagen final en grayscale dividida en 4 cuadrantes

## Ejercicio 4 - Captura con tecla 'f' (OOP)
```bash
python ejercicio3_4_captura.py --mode keypress
```
- Igual que ejercicio 3 pero solo captura al presionar `f`

---

## Ejercicio 5 - Detección de contornos en imagen
```bash
python ejercicio5_contornos.py imagen.jpg   # con imagen propia
python ejercicio5_contornos.py              # imagen de prueba generada
```

---

## Ejercicio 6 - Contornos en tiempo real (webcam)
```bash
python ejercicio6_contornos_realtime.py
```
- Compatible laptop y Raspberry Pi
- En RPi: resolución 320x240 ya configurada para mejor rendimiento
- **Diferencia observada en RPi**: FPS reducido (~5-15 fps vs ~30 fps en laptop)

---

## Ejercicio 7 - Semáforo + Motor (Pico 2W)

### Archivo: `ejercicio7_semaforo_pico2w.py` → subir al Pico con Thonny

### Conexiones Pico 2W:
```
GP13 -> LED Verde  (+ resistencia 220Ω)
GP14 -> LED Amarillo (+ resistencia 220Ω)
GP15 -> LED Rojo   (+ resistencia 220Ω)
GP16 -> IN1 del driver L298N (señal PWM para motor)
GND  -> GND común
```

### Ciclo:
- Verde (10s) → Motor 100%
- Amarillo (10s) → Motor 25%
- Rojo (10s) → Motor OFF

---

## Ejercicio 8 - Detección de movimiento + Alarma

### Parte A (PC/RPi):
```bash
# Linux/RPi:
python ejercicio8_movimiento_pc.py /dev/ttyACM0

# Sin hardware serial (solo visión):
python ejercicio8_movimiento_pc.py
```

### Parte B (Pico 2W): subir `ejercicio8_buzzer_pico2w.py` con Thonny

### Conexiones Pico 2W:
```
GP17 -> Buzzer activo (+)
GP0  -> UART TX (-> RX del host)
GP1  -> UART RX (<- TX del host)
GND  -> GND común con PC/RPi
```

### Protocolo UART:
- `'1'` → Buzzer ON (movimiento detectado)
- `'0'` → Buzzer OFF

---

## Ejercicio 9 - Conteo de objetos + LEDs

### Parte A (PC/RPi):
```bash
python ejercicio9_objetos_pc.py /dev/ttyACM0
```

### Parte B (Pico 2W): subir `ejercicio9_leds_pico2w.py` con Thonny

### Conexiones Pico 2W:
```
GP2  -> LED 1 (+ resistencia 220Ω)
GP3  -> LED 2 (+ resistencia 220Ω)
GP4  -> LED 3 (+ resistencia 220Ω)
GP5  -> LED 4 (+ resistencia 220Ω)
GP17 -> Buzzer activo (+)
GP0  -> UART TX
GP1  -> UART RX
GND  -> GND común
```

### Lógica:
| Objetos | LEDs | Buzzer |
|---------|------|--------|
| 0 | Todos OFF | OFF |
| 1 | 2 LEDs ON | ON |
| >1 | Todos ON | ON |

---

## Notas generales
- Puerto serial en Windows: usar `COM3`, `COM4`, etc. (ver Device Manager)
- Puerto serial en Linux/RPi: `/dev/ttyACM0` o `/dev/ttyUSB0`
- Para subir código MicroPython al Pico 2W: usar **Thonny IDE**
- Driver motor recomendado: L298N o L9110S
- El Pico 2W opera a **3.3V** en sus GPIOs — no conectar directamente a 5V
