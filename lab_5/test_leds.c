#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/rom_map.h"

int main(void) {
    MAP_SysCtlClockFreqSet(
        SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
        SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240,
        120000000);

    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));

    MAP_GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, 0x03);
    MAP_GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, 0x11);

    // Encender todos los LEDs
    MAP_GPIOPinWrite(GPIO_PORTN_BASE, 0x03, 0x03);
    MAP_GPIOPinWrite(GPIO_PORTF_BASE, 0x11, 0x11);

    while(1);
}
