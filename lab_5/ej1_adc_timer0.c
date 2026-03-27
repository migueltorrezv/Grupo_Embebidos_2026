// ============================================================
// Ejercicio 1: Potenciometro controla velocidad de secuencia
//              de LEDs via ADC (AIN19/PK3) + Timer 0
// Hardware: TM4C1294XL
// Conexiones:
//   Pot VCC  -> 3.3V
//   Pot Wiper-> PK3 (AIN19)
//   Pot GND  -> GND
//   LED PN0  -> PN0 -> 330ohm -> GND
//   LED PN1  -> PN1 -> 330ohm -> GND
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

volatile uint8_t led_state = 0;  // estado actual de la secuencia

// ISR Timer0: avanza secuencia de LEDs (00 -> 01 -> 10 -> 11 -> 00...)
void Timer0A_Handler(void) {
    TimerIntClear(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    led_state = (led_state + 1) % 4;
    GPIOPinWrite(GPIO_PORTN_BASE, 0x03, led_state);
}

void ADC0_Init(void) {
    SysCtlPeripheralEnable(SYSCTL_PERIPH_ADC0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOK);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_ADC0));

    // PK3 como entrada analogica (AIN19)
    GPIOPinTypeADC(GPIO_PORTK_BASE, 0x08);

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
    SysCtlPeripheralEnable(SYSCTL_PERIPH_TIMER0);
    TimerConfigure(TIMER0_BASE, TIMER_CFG_PERIODIC);
    TimerIntRegister(TIMER0_BASE, TIMER_A, Timer0A_Handler);
    TimerIntEnable(TIMER0_BASE, TIMER_TIMA_TIMEOUT);
    IntMasterEnable();
}

int main(void) {
    // Reloj sistema 120 MHz
    SysCtlClockFreqSet(
        SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
        SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480,
        120000000);

    ADC0_Init();
    Timer0_Init();

    // LEDs PN0 y PN1 como salidas
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, 0x03);

    while(1) {
        uint32_t adc_val = ADC_Read();  // 0 - 4095

        // Mapear ADC a periodo: pot al maximo = 0.1s (rapido)
        //                        pot al minimo = 1.0s (lento)
        float periodo_s = 0.1f + (1.0f - (float)adc_val / 4095.0f) * 0.9f;
        uint32_t ticks = (uint32_t)(120000000.0f * periodo_s);

        // Recargar y habilitar timer con nuevo periodo
        TimerLoadSet(TIMER0_BASE, TIMER_A, ticks - 1);
        TimerEnable(TIMER0_BASE, TIMER_A);

        // Esperar ~100ms antes de releer el potenciometro
        SysCtlDelay(120000000 / 30);
    }
}
