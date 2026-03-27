// ============================================================
// Ejercicio 1: Potenciometro controla velocidad de secuencia
//              de LEDs via ADC (AIN19/PK3) + Timer 0
// Hardware: TM4C1294XL
// Conexiones:
//   Pot VCC   -> 3.3V
//   Pot Wiper -> PK3 (AIN19)
//   Pot GND   -> GND
//   LEDs PN0, PN1 -> integrados en placa
// Compilar con: startup_gcc.c incluido en Makefile
// ============================================================

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
volatile uint8_t led_state = 0;

// ISR Timer0: avanza secuencia de LEDs (00->01->10->11->00...)
void Timer0A_Handler(void) {
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    led_state = (led_state + 1) % 4;
    MAP_GPIOPinWrite(GPIO_PORTN_BASE, 0x03, led_state);
}

void ADC0_Init(void) {
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_ADC0);
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOK);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_ADC0));
    // PK3 como entrada analogica (AIN19)
    MAP_GPIOPinTypeADC(GPIO_PORTK_BASE, 0x08);
    // Sequencer 3: 1 muestra, trigger por software, prioridad 0
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
    return val;  // 0 a 4095
}

void Timer0_Init(void) {
    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
    TimerIntRegister(TIMER0_BASE, TIMER_A, Timer0A_Handler);
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    MAP_IntMasterEnable();
}

int main(void) {
    g_ui32SysClock = MAP_SysCtlClockFreqSet(
        SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
        SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240,
        120000000);

    ADC0_Init();
    Timer0_Init();

    MAP_SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    while(!MAP_SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    MAP_GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, 0x03);

    while(1) {
        uint32_t adc_val = ADC_Read();  // 0 - 4095

        // pot maximo = 0.1s (rapido), pot minimo = 1.0s (lento)
        float periodo_s = 0.1f + (1.0f - (float)adc_val / 4095.0f) * 0.9f;
        uint32_t ticks = (uint32_t)(g_ui32SysClock * periodo_s);

        TimerLoadSet(TIMER0_BASE, TIMER_A, ticks - 1);
        TimerEnable(TIMER0_BASE, TIMER_A);

        MAP_SysCtlDelay(g_ui32SysClock / 30);
    }
}
