#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "inc/hw_ints.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"
#include "driverlib/timer.h"
#include "driverlib/interrupt.h"

// 🔥 Tiempo: 2 segundos
#define FS (120000000 * 5)

// Contador global
volatile uint8_t counter = 0;

//================= MOSTRAR EN LEDS =================
void mostrar(uint8_t counter)
{
    uint8_t ledsN = 0;
    uint8_t ledsF = 0;

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

//================= ISR =================
void tipulatimer(void)
{
    // Limpiar interrupción
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);

    // Incrementar contador (0–15)
    counter++;

    if(counter > 15)
        counter = 0;

    // Mostrar en LEDs
    mostrar(counter);
}

//================= MAIN =================
int main(void)
{
    // Reloj 120 MHz
    SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ |
                        SYSCTL_OSC_MAIN |
                        SYSCTL_USE_PLL |
                        SYSCTL_CFG_VCO_480), 120000000);

    // Activar puertos
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);

    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));

    // LEDs como salida
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4);

    // Activar Timer0
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));

    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);

    // Tiempo (2 segundos)
    TimerLoadSet(TIMER0_BASE, TIMER_A, FS - 1);

    // Interrupciones
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    IntEnable(INT_TIMER0A);
    IntMasterEnable();

    // Iniciar timer
    TimerEnable(TIMER0_BASE, TIMER_A);

    while(1)
    {
        // vacío (todo lo hace la ISR)
    }
}