#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "inc/hw_ints.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"
#include "driverlib/timer.h"
#include "driverlib/interrupt.h"

// Frecuencia de TIVA
#define FS (120000000 * 4)   // Aqui podemos cambiar el tiempo delay

// Variable global
volatile uint8_t estado = 0;

// ISR
void tipulatimer(void);

int main(void)
{
    // Configuracion del Clock
    SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ |
                        SYSCTL_OSC_MAIN |
                        SYSCTL_USE_PLL |
                        SYSCTL_CFG_VCO_480), 120000000);

    // Activar GPIO N
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));

    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_1);

    // Activar Timer0
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));

    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);

    TimerLoadSet(TIMER0_BASE, TIMER_A, FS - 1);

    // Interrupciones
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    IntEnable(INT_TIMER0A);
    IntMasterEnable();

    // Iniciamos TIMER
    TimerEnable(TIMER0_BASE, TIMER_A);

    while(1)
    {
        
    }
}

// ================= ISR =================
void tipulatimer(void)
{
    // Limpiar interrupción
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);

    // Cambiar estado del LED
    estado ^= 1;

    if(estado)
        GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, GPIO_PIN_1);
    else
        GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, 0);
}