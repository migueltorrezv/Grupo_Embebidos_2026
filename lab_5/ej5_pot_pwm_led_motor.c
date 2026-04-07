# Ejercicio 5 - Tiva, control led y motor

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include "inc/hw_memmap.h"
#include "driverlib/gpio.h"
#include "driverlib/pin_map.h"
#include "driverlib/pwm.h"
#include "driverlib/sysctl.h"
#include "driverlib/adc.h"

uint32_t g_ui32SysClock;
uint32_t ui32ADC0Value[1]; // Almacena el valor del potenciómetro

// Función para configurar el reloj del sistema
void configureSystemClock(void) {
    g_ui32SysClock = SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
                                         SYSCTL_USE_PLL | SYSCTL_CFG_VCO_480), 120000000);
}







// Función para configurar el ADC (Potenciómetro en PE3)
void configureADC(void) {
    SysCtlPeripheralEnable(SYSCTL_PERIPH_ADC0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
    
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_ADC0)) {}
    
    // PE3 es el canal 0 del ADC (AIN0)
    GPIOPinTypeADC(GPIO_PORTE_BASE, GPIO_PIN_3);
    
    // Configurar secuencia 3 (una sola muestra)
    ADCSequenceConfigure(ADC0_BASE, 3, ADC_TRIGGER_PROCESSOR, 0);
    ADCSequenceStepConfigure(ADC0_BASE, 3, 0, ADC_CTL_CH0 | ADC_CTL_IE | ADC_CTL_END);
    ADCSequenceEnable(ADC0_BASE, 3);
}








void configurePWM(void) {
    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);

    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_PWM0)) {}
    
    // PF1 para LED externo o ENA del motor
    // PF2 y PF3 para IN1 e IN2 (Dirección)
    GPIOPinConfigure(GPIO_PF1_M0PWM1);
    GPIOPinTypePWM(GPIO_PORTF_BASE, GPIO_PIN_1);
    
    // Configurar PF2 y PF3 como salidas digitales para el motor
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_2 | GPIO_PIN_3);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2, GPIO_PIN_2); // IN1 = HIGH
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_3, 0);          // IN2 = LOW

    PWMClockSet(PWM0_BASE, PWM_SYSCLK_DIV_16);
    PWMGenConfigure(PWM0_BASE, PWM_GEN_0, PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);

    // Usamos 100 para que el duty cycle sea directamente el porcentaje
    uint32_t period = 100; 
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, period);

    PWMOutputState(PWM0_BASE, PWM_OUT_1_BIT, true);
    PWMGenEnable(PWM0_BASE, PWM_GEN_0);
}








int main(void) {
    // Llamar a las funciones para inicializar el sistema
    configureSystemClock();
    configurePWM();
    configureADC();

    
    while (1) {
        // 1. Disparar el ADC para leer el potenciómetro
        ADCProcessorTrigger(ADC0_BASE, 3);
        while(!ADCIntStatus(ADC0_BASE, 3, false)) {}
        ADCIntClear(ADC0_BASE, 3);
        ADCSequenceDataGet(ADC0_BASE, 3, ui32ADC0Value);

        // 2. Mapear valor del ADC (0-4095) a Duty Cycle (1-99)
        // La Tiva tiene 12 bits, por eso el máximo es 4095
        uint32_t duty = (ui32ADC0Value[0] * 99) / 4095;
        
        if (duty < 1) duty = 1; // Para que no se apague del todo si no quieres

        // 3. Actualizar la intensidad del LED / Velocidad del Motor
        PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, duty);
        GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_2 | GPIO_PIN_3, GPIO_PIN_2);
        // 4. Pausa de 0.5 segundos (Requisito del Ejercicio)
        SysCtlDelay(g_ui32SysClock / 6);
    
    
    }
}
