// ============================================================
// Ejercicio 2 - TIVA TM4C1294XL
// Recibe distancia via UART desde RPi y controla LEDs de usuario
//
// Conexiones UART:
//   USB microUSB TIVA -> Puerto USB RPi (/dev/ttyACM0)
//
// LEDs de usuario TM4C1294XL (integrados en placa):
//   PN0 -> LED D2
//   PN1 -> LED D1
//   PF0 -> LED D4
//   PF4 -> LED D3
//
// Logica de distancia:
//   dist > 10 cm        -> todos apagados
//   8  < dist <= 10 cm  -> PN1
//   6  < dist <= 8  cm  -> PN1 + PN0
//   4  < dist <= 6  cm  -> PN1 + PN0 + PF4
//   dist <= 4 cm        -> todos encendidos
//
// Compilar con: startup_gcc.c incluido en Makefile
// Baud rate: 115200
// ============================================================

#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "inc/hw_memmap.h"
#include "inc/hw_ints.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/uart.h"
#include "driverlib/pin_map.h"
#include "driverlib/interrupt.h"
#include "driverlib/rom_map.h"
#include "utils/uartstdio.c"

#define LED_PN1  0x02
#define LED_PN0  0x01
#define LED_PF4  0x10
#define LED_PF0  0x01

uint32_t g_ui32SysClock;

void GPIO_LEDs_Init(void) {
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    MAP_GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, LED_PN0 | LED_PN1);
    MAP_GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, LED_PF0 | LED_PF4);
}

void set_leds(uint8_t pn_val, uint8_t pf_val) {
    MAP_GPIOPinWrite(GPIO_PORTN_BASE, LED_PN0 | LED_PN1, pn_val);
    MAP_GPIOPinWrite(GPIO_PORTF_BASE, LED_PF0 | LED_PF4, pf_val);
}

void UART0_Init(void) {
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    MAP_GPIOPinConfigure(GPIO_PA0_U0RX);
    MAP_GPIOPinConfigure(GPIO_PA1_U0TX);
    MAP_GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTStdioConfig(0, 115200, g_ui32SysClock);
}

int main(void) {
    g_ui32SysClock = MAP_SysCtlClockFreqSet(
        SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
        SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240,
        120000000);

    GPIO_LEDs_Init();
    UART0_Init();

    char buf[32];

    while(1) {
        UARTgets(buf, sizeof(buf));

        // Limpiar \r \n y espacios
        int i = 0;
        while(buf[i] != '\0') {
            if(buf[i] == '\r' || buf[i] == '\n' || buf[i] == ' ')
                buf[i] = '\0';
            i++;
        }

        float dist = (float)atof(buf);
        UARTprintf("Recibido: %s -> %.1f cm\n", buf, dist);

        if (dist > 10.0f) {
            set_leds(0x00, 0x00);
        } else if (dist > 8.0f) {
            set_leds(LED_PN1, 0x00);
        } else if (dist > 6.0f) {
            set_leds(LED_PN1 | LED_PN0, 0x00);
        } else if (dist > 4.0f) {
            set_leds(LED_PN1 | LED_PN0, LED_PF4);
        } else {
            set_leds(LED_PN1 | LED_PN0, LED_PF4 | LED_PF0);
        }
    }
}
