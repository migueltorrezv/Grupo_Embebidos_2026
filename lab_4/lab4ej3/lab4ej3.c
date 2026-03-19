#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "inc/hw_ints.h"
#include "inc/hw_gpio.h"
#include "inc/hw_types.h"
#include "driverlib/gpio.h"
#include "driverlib/sysctl.h"
#include "driverlib/timer.h"
#include "driverlib/interrupt.h"

#define FREQ   120000000
#define T_2S   (FREQ * 2)
#define T_05S  (FREQ / 2)

volatile uint8_t flag = 0;
volatile uint8_t modo = 0;

void tipulatimer(void) {
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    flag = 1;
    static uint8_t last = 1;
    uint8_t current = GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0);
    if(last == 1 && current == 0) {
        modo ^= 1;
        if(modo == 0) TimerLoadSet(TIMER0_BASE, TIMER_A, T_2S - 1);
        else TimerLoadSet(TIMER0_BASE, TIMER_A, T_05S - 1);
    }
    last = current;
}

void mostrar(uint8_t counter) {

    uint8_t ledsN = 0, ledsF = 0; 
    
    if(counter & 0x01) ledsN |= GPIO_PIN_1;
    if(counter & 0x02) ledsN |= GPIO_PIN_0;
    if(counter & 0x04) ledsF |= GPIO_PIN_4;
    if(counter & 0x08) ledsF |= GPIO_PIN_0;
    
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, ledsN);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4, ledsF);
}

int main(void) {
    uint8_t counter = 0;
    SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480), FREQ);
    
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));

    HWREG(GPIO_PORTF_BASE + GPIO_O_LOCK) = 0x4C4F434B;
    HWREG(GPIO_PORTF_BASE + GPIO_O_CR) |= GPIO_PIN_0;
    
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0 | GPIO_PIN_4);
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0, GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);
    
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_TIMER0));
    
    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
    TimerLoadSet(TIMER0_BASE, TIMER_A, T_2S - 1);
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    IntEnable(INT_TIMER0A);
    IntMasterEnable();
    TimerEnable(TIMER0_BASE, TIMER_A);
    
    mostrar(counter);
    
    while(1) {
        if(flag) {
            flag = 0;
            counter++;
            if(counter > 10) counter = 0;
            mostrar(counter);
        }
    }
}