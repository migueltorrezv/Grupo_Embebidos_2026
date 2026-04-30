# LABORATORIO 8 - Ejercicio 7
# Semáforo con Raspberry Pi Pico 2W (MicroPython)
# + Control de motor PWM desde Raspberry Pi (via UART o standalone)
#
# Conexiones Pico 2W:
#   LED Rojo   -> GP15
#   LED Amarillo -> GP14
#   LED Verde  -> GP13
#   Motor PWM  -> GP16 (señal PWM para driver L298N o similar)
#   GND        -> GND
#
# El Pico 2W maneja LEDs y motor directamente.
# (Reemplaza al sistema TIVA + Raspberry Pi del enunciado original)

import machine
import time
import utime

# --- Configuración de pines ---
LED_RED    = machine.Pin(15, machine.Pin.OUT)
LED_YELLOW = machine.Pin(14, machine.Pin.OUT)
LED_GREEN  = machine.Pin(13, machine.Pin.OUT)

# PWM para motor (frecuencia 1kHz)
motor_pwm = machine.PWM(machine.Pin(16))
motor_pwm.freq(1000)

# Duty cycle: 0-65535 en MicroPython
DUTY_100 = 65535   # 100%
DUTY_25  = 16383   # 25%
DUTY_0   = 0       # Parado


def all_leds_off():
    LED_RED.value(0)
    LED_YELLOW.value(0)
    LED_GREEN.value(0)


def set_green():
    """Verde encendido -> Motor 100%"""
    all_leds_off()
    LED_GREEN.value(1)
    motor_pwm.duty_u16(DUTY_100)
    print("VERDE -> Motor 100%")


def set_yellow():
    """Amarillo encendido -> Motor 25%"""
    all_leds_off()
    LED_YELLOW.value(1)
    motor_pwm.duty_u16(DUTY_25)
    print("AMARILLO -> Motor 25%")


def set_red():
    """Rojo encendido -> Motor parado"""
    all_leds_off()
    LED_RED.value(1)
    motor_pwm.duty_u16(DUTY_0)
    print("ROJO -> Motor parado")


def traffic_light_cycle():
    """Ciclo infinito del semáforo: Verde -> Amarillo -> Rojo, 10s cada uno."""
    print("Iniciando ciclo de semáforo...")
    while True:
        set_green()
        utime.sleep(10)

        set_yellow()
        utime.sleep(10)

        set_red()
        utime.sleep(10)


# --- Entry point ---
if __name__ == '__main__':
    try:
        traffic_light_cycle()
    except KeyboardInterrupt:
        # Limpieza al salir
        all_leds_off()
        motor_pwm.duty_u16(DUTY_0)
        print("Programa terminado.")
