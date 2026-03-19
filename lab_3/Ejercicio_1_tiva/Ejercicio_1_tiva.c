#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"

void delay(void)
{
    volatile uint32_t i;
    for(i = 0; i < 300000; i++);
}

int main(void)
{
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));

    // LEDs
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4);

    // Botones
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1,
                     GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);

    uint8_t estado = 0;

    // Variables para guardar estado real de LEDs
    uint8_t ledsN = 0;
    uint8_t ledsF = 0;

    while(1)
    {
        // 🔼 ENCENDER UNO A UNO
        if(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) == 0)
        {
            delay();
            while(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) == 0);

            if(estado == 0) ledsN |= GPIO_PIN_1; // PN1
            else if(estado == 1) ledsN |= GPIO_PIN_0; // PN0
            else if(estado == 2) ledsF |= GPIO_PIN_4; // PF4
            else if(estado == 3) ledsF |= GPIO_PIN_0; // PF0

            if(estado < 4) estado++;
        }

        // 🔽 APAGAR UNO A UNO
        if(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_1) == 0)
        {
            delay();
            while(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_1) == 0);

            if(estado == 4) ledsF &= ~GPIO_PIN_0; // PF0
            else if(estado == 3) ledsF &= ~GPIO_PIN_4; // PF4
            else if(estado == 2) ledsN &= ~GPIO_PIN_0; // PN0
            else if(estado == 1) ledsN &= ~GPIO_PIN_1; // PN1

            if(estado > 0) estado--;
        }

        // ACTUALIZAR LEDs (sin perder estado)
        GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, ledsN);
        GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4, ledsF);
    }
}