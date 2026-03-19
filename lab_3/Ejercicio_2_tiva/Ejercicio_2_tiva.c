//*****************************************************************************
//
// LABORATORIO #3 - EJERCICIO #2 (CORREGIDO)
//
//*****************************************************************************

#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/debug.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"

uint32_t ui32SysClock; //  DECLARADO

#ifdef DEBUG
void __error__(char *pcFilename, uint32_t ui32Line)
{
    while(1);
}
#endif

// Delay en milisegundos
void delay_ms(uint32_t ms)
{
    SysCtlDelay((ui32SysClock / 3 / 1000) * ms);
}

// Apagar todos los LEDs
void led_off()
{
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, 0);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4, 0);
}

int main(void)
{
    // Configurar reloj a 120 MHz
    ui32SysClock = SysCtlClockFreqSet(
        (SYSCTL_XTAL_25MHZ |
         SYSCTL_OSC_MAIN |
         SYSCTL_USE_PLL |
         SYSCTL_CFG_VCO_480),
         120000000);

    // Habilitar puertos
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));

    // Configurar LEDs como salida
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4);

    while(1)
    {
        // 🔹 Estado 1 → PN1
        led_off();
        GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, GPIO_PIN_1);
        delay_ms(2000);

        // 🔹 Estado 2 → PN0
        led_off();
        GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0, GPIO_PIN_0);
        delay_ms(2000);

        // 🔹 Estado 3 → PF4
        led_off();
        GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_4, GPIO_PIN_4);
        delay_ms(2000);

        // 🔹 Estado 4 → PF0
        led_off();
        GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, GPIO_PIN_0);
        delay_ms(2000);
    }
}
