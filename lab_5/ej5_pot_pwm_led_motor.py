# ============================================================
# Ejercicio 5 - Raspberry Pi 4
# Potenciometro -> MCP3008 (ADC SPI) -> PWM -> LED externo
# Para motor DC: cambiar LED_PIN = 18 por ENA = 12
#                y agregar IN1/IN2 igual que ejercicio 3
#
# Conexiones MCP3008 -> RPi:
#   VDD    (pin 16) -> 3.3V     (Pin 1)
#   VREF   (pin 15) -> 3.3V     (Pin 1)
#   AGND   (pin 14) -> GND      (Pin 9)
#   DGND   (pin  9) -> GND      (Pin 9)
#   CLK    (pin 13) -> GPIO11   (Pin 23) SCLK
#   DOUT   (pin 12) -> GPIO9    (Pin 21) MISO
#   DIN    (pin 11) -> GPIO10   (Pin 19) MOSI
#   CS     (pin 10) -> GPIO8    (Pin 24) CE0
#   CH0    (pin  1) -> Pot wiper
#   Pot VCC         -> 3.3V
#   Pot GND         -> GND
#
# Conexiones LED externo:
#   GPIO18 (Pin 12) -> 330ohm -> LED anodo -> LED catodo -> GND
#
# Activar SPI: sudo raspi-config -> Interface Options -> SPI -> Enable
# ============================================================

import RPi.GPIO as GPIO
import spidev
from time import sleep

LED_PIN = 18  # cambiar a 12 (ENA L298N) para motor DC

# SPI para MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)           # bus 0, device 0 (CE0 = GPIO8)
spi.max_speed_hz = 1000000

def leer_adc(canal):
    """Lee canal 0-7 del MCP3008. Retorna 0-1023."""
    r = spi.xfer2([1, (8 + canal) << 4, 0])
    return ((r[1] & 3) << 8) + r[2]

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

pwm = GPIO.PWM(LED_PIN, 1000)  # 1 kHz
pwm.start(0)

try:
    while True:
        valor = leer_adc(0)                   # CH0 del MCP3008 (0-1023)
        duty  = (valor / 1023.0) * 100.0      # mapear a 0-100%
        pwm.ChangeDutyCycle(duty)
        print(f"ADC: {valor:4d} | Duty: {duty:5.1f}%")
        sleep(0.5)

except KeyboardInterrupt:
    print("Deteniendo...")
finally:
    pwm.stop()
    spi.close()
    GPIO.cleanup()
