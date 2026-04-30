# LABORATORIO 8 - Ejercicio 8 (Parte B)
# Raspberry Pi Pico 2W - MicroPython
# Recibe señal UART desde PC/RPi y activa buzzer como alarma.
#
# Conexiones Pico 2W:
#   Buzzer activo (+) -> GP17
#   Buzzer GND        -> GND
#   UART RX           -> GP1  (UART0 RX) <- conectar al TX del dispositivo host
#   UART TX           -> GP0  (UART0 TX) <- conectar al RX del dispositivo host
#   GND común con host
#
# Protocolo: recibe '1' -> buzzer ON, '0' -> buzzer OFF

import machine
import utime

# --- Pines ---
buzzer = machine.Pin(17, machine.Pin.OUT)
led_builtin = machine.Pin("LED", machine.Pin.OUT)  # LED integrado del Pico W

# --- UART ---
uart = machine.UART(0, baudrate=9600, tx=machine.Pin(0), rx=machine.Pin(1))


def buzzer_on():
    buzzer.value(1)
    led_builtin.value(1)


def buzzer_off():
    buzzer.value(0)
    led_builtin.value(0)


def beep_pattern():
    """Patrón de pitido de alarma."""
    for _ in range(3):
        buzzer.value(1)
        utime.sleep_ms(200)
        buzzer.value(0)
        utime.sleep_ms(100)


print("Pico 2W listo. Esperando señal de movimiento...")

while True:
    if uart.any():
        data = uart.read(1)
        if data == b'1':
            print("Movimiento detectado -> ALARMA ON")
            buzzer_on()
        elif data == b'0':
            print("Sin movimiento -> ALARMA OFF")
            buzzer_off()

    utime.sleep_ms(50)
