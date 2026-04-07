// Ejercicio 1: Potenciometro 5k controla velocidad secuencia
#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/adc.h"
#include "driverlib/timer.h"
#include "driverlib/interrupt.h"
#include "driverlib/pin_map.h"
#include "driverlib/rom_map.h"

uint32_t g_ui32SysClock;
volatile uint8_t  led_state = 0;
volatile uint32_t g_ticks   = 0; 

void Timer0A_Handler(void) {
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);

    led_state = (led_state + 1) % 4;

    MAP_GPIOPinWrite(GPIO_PORTN_BASE, 0x03, 0x00);
    MAP_GPIOPinWrite(GPIO_PORTF_BASE, 0x11, 0x00);

    switch(led_state) {
        case 0: MAP_GPIOPinWrite(GPIO_PORTN_BASE, 0x03, 0x02); break; // PN1
        case 1: MAP_GPIOPinWrite(GPIO_PORTN_BASE, 0x03, 0x01); break; // PN0
        case 2: MAP_GPIOPinWrite(GPIO_PORTF_BASE, 0x11, 0x10); break; // PF4
        case 3: MAP_GPIOPinWrite(GPIO_PORTF_BASE, 0x11, 0x01); break; // PF0
    }


    TimerLoadSet(TIMER0_BASE, TIMER_A, g_ticks - 1);
}

void ADC0_Init(void) {
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_ADC0);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOK);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_ADC0));
    MAP_GPIOPinTypeADC(GPIO_PORTK_BASE, 0x08);  // PK3 = AIN19
    ADCSequenceConfigure(ADC0_BASE, 3, ADC_TRIGGER_PROCESSOR, 0);
    ADCSequenceStepConfigure(ADC0_BASE, 3, 0,
                             ADC_CTL_IE | ADC_CTL_END | ADC_CTL_CH19);
    ADCSequenceEnable(ADC0_BASE, 3);
    ADCIntClear(ADC0_BASE, 3);
}

uint32_t ADC_Read(void) {
    uint32_t val;
    ADCProcessorTrigger(ADC0_BASE, 3);
    while(!ADCIntStatus(ADC0_BASE, 3, false));
    ADCIntClear(ADC0_BASE, 3);
    ADCSequenceDataGet(ADC0_BASE, 3, &val);
    return val;
}

int main(void) {
    g_ui32SysClock = MAP_SysCtlClockFreqSet(
        SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
        SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240,
        120000000);

    ADC0_Init();

    // LEDs
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    MAP_GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, 0x03);

    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    MAP_GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, 0x11);

    // Timer
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
    TimerIntRegister(TIMER0_BASE, TIMER_A, Timer0A_Handler);
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    MAP_IntMasterEnable();

    g_ticks = g_ui32SysClock / 2;
    TimerLoadSet(TIMER0_BASE, TIMER_A, g_ticks - 1);
    TimerEnable(TIMER0_BASE, TIMER_A);

    MAP_GPIOPinWrite(GPIO_PORTN_BASE, 0x03, 0x02);

    while(1) {
        uint32_t adc_val = ADC_Read();  // 0 a 4095

        float ratio = 1.0f - ((float)adc_val / 4095.0f);
        g_ticks = (uint32_t)(g_ui32SysClock * (0.1f + ratio * 0.9f));
        
        MAP_SysCtlDelay(g_ui32SysClock / 30);
    }
}
