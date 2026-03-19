#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"

uint32_t ui32SysClock;

void delay(void)
{
    SysCtlDelay(ui32SysClock / 10); // pequeño anti-rebote
}

// Mostrar el valor binario en LEDs
void mostrar(uint8_t counter)
{
    uint8_t ledsN = 0;
    uint8_t ledsF = 0;

    // Bits:
    // bit0 → PN1
    // bit1 → PN0
    // bit2 → PF4
    // bit3 → PF0

    if(counter & 0x01) ledsN |= GPIO_PIN_1;
    if(counter & 0x02) ledsN |= GPIO_PIN_0;
    if(counter & 0x04) ledsF |= GPIO_PIN_4;
    if(counter & 0x08) ledsF |= GPIO_PIN_0;

    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, ledsN);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4, ledsF);
}

int main(void)
{
    ui32SysClock = SysCtlClockFreqSet(
        (SYSCTL_XTAL_25MHZ |
         SYSCTL_OSC_MAIN |
         SYSCTL_USE_PLL |
         SYSCTL_CFG_VCO_480),
         120000000);

    // Habilitar puertos
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));

    // LEDs
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4);

    // Botones
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1,
                     GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);

    uint8_t counter = 0;

    while(1)
    {
        // 🔼 Incrementar
        if(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) == 0)
        {
            delay();
            while(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0) == 0);

            if(counter < 15)
                counter++;

            mostrar(counter);
        }

        // 🔽 Decrementar
        if(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_1) == 0)
        {
            delay();
            while(GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_1) == 0);

            if(counter > 0)
                counter--;

            mostrar(counter);
        }
    }
}