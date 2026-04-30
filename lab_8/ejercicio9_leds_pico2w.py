# LABORATORIO 8 - Ejercicio 9 (Parte B)
# Raspberry Pi Pico 2W - MicroPython
# Controla 4 LEDs según número de objetos detectados por la cámara.
#
# Conexiones Pico 2W:
#   LED 1  -> GP2
#   LED 2  -> GP3
#   LED 3  -> GP4
#   LED 4  -> GP5
#   Buzzer -> GP17 (herencia del ejercicio 8)
#   UART RX -> GP1
#   UART TX -> GP0
#   Todos los GND -> GND común
#
# Protocolo UART:
#   '0' -> 0 objetos -> todos LEDs OFF, buzzer OFF
#   '1' -> 1 objeto  -> 2 LEDs ON, buzzer ON
#   '2' -> >1 objeto -> todos LEDs ON, buzzer ON

import machine
import utime

# --- Pines LEDs ---
led1 = machine.Pin(2, machine.Pin.OUT)
led2 = machine.Pin(3, machine.Pin.OUT)
led3 = machine.Pin(4, machine.Pin.OUT)
led4 = machine.Pin(5, machine.Pin.OUT)
LEDS = [led1, led2, led3, led4]

buzzer = machine.Pin(17, machine.Pin.OUT)
led_builtin = machine.Pin("LED", machine.Pin.OUT)

uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))


def all_off():
    for led in LEDS:
        led.value(0)
    buzzer.value(0)
    led_builtin.value(0)


def two_leds_on():
    """1 objeto detectado -> encender 2 LEDs + buzzer."""
    all_off()
    led1.value(1)
    led2.value(1)
    buzzer.value(1)
    led_builtin.value(1)


def all_leds_on():
    """Más de 1 objeto -> encender todos los LEDs + buzzer."""
    for led in LEDS:
        led.value(1)
    buzzer.value(1)
    led_builtin.value(1)


# --- Startup blink ---
print("Pico 2W listo. Esperando datos de objeto...")
for led in LEDS:
    led.value(1)
    utime.sleep_ms(100)
    led.value(0)

all_off()

# --- Loop principal ---
while True:
    if uart.any():
        data = uart.read(1)

        if data == b'0':
            print("Sin objetos -> Todo OFF")
            all_off()

        elif data == b'1':
            print("1 objeto -> 2 LEDs + buzzer ON")
            two_leds_on()

        elif data == b'2':
            print(">1 objeto -> Todos LEDs + buzzer ON")
            all_leds_on()

    utime.sleep_ms(50)
