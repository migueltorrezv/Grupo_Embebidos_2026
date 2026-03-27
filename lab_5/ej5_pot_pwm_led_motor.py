# ============================================================
# Ejercicio 5 - Raspberry Pi 4
# Potenciometro -> MCP3008 (ADC SPI) -> PWM -> LED externo
# Despues cambiar LED_PIN por ENA del L298N para motor DC
#
# Conexiones MCP3008 -> RPi:
#   VDD  (16) -> 3.3V
#   VREF (15) -> 3.3V
#   AGND (14) -> GND
#   DGND  (9) -> GND
#   CLK  (13) -> GPIO11 (SCLK)
#   DOUT (12) -> GPIO9  (MISO)
#   DIN  (11) -> GPIO10 (MOSI)
#   CS    (10) -> GPIO8  (CE0)
#   CH0   (1) -> Potenciometro wiper
#   Pot VCC   -> 3.3V
#   Pot GND   -> GND
#
# Conexiones LED externo:
#   GPIO18 -> 330ohm -> LED anodo
#   LED catodo -> GND
#
# Para motor DC: cambiar LED_PIN = 18 por ENA = 12
#   y agregar IN1/IN2 como en ejercicio 3
# ============================================================

import RPi.GPIO as GPIO
import spidev
from time import sleep

LED_PIN = 18  # cambiar a 12 (ENA L298N) para motor DC

# Inicializar SPI para MCP3008
spi = spidev.SpiDev()
spi.open(0, 0)          # bus 0, device 0 (CE0 = GPIO8)
spi.max_speed_hz = 1000000

def leer_adc(canal):
    """Lee canal 0-7 del MCP3008. Retorna valor 0-1023."""
    r = spi.xfer2([1, (8 + canal) << 4, 0])
    return ((r[1] & 3) << 8) + r[2]

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

pwm = GPIO.PWM(LED_PIN, 1000)  # 1 kHz
pwm.start(0)

try:
    while True:
        valor = leer_adc(0)                  # leer CH0 del MCP3008 (0-1023)
        duty = (valor / 1023.0) * 100.0      # mapear a 0-100%
        pwm.ChangeDutyCycle(duty)
        print(f"ADC: {valor:4d} | Duty: {duty:5.1f}%")
        sleep(0.5)  # actualizar cada 0.5 segundos

except KeyboardInterrupt:
    print("Deteniendo...")
finally:
    pwm.stop()
    spi.close()
    GPIO.cleanup()
