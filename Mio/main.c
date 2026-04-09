#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/uart.h"
#include "driverlib/pin_map.h"
#include "driverlib/pwm.h"
#include "inc/hw_types.h"

uint32_t g_ui32SysClock;

void UARTSendString(const char *str) {
    while (*str) UARTCharPut(UART0_BASE, *str++);
}

void UARTSendInt(uint32_t val) {
    char buf[12];
    int i = 0;
    if (val == 0) { UARTCharPut(UART0_BASE, '0'); return; }
    while (val > 0) { buf[i++] = '0' + (val % 10); val /= 10; }
    for (int j = i-1; j >= 0; j--) UARTCharPut(UART0_BASE, buf[j]);
}

void delay_ms(uint32_t ms) {
    SysCtlDelay((g_ui32SysClock / 3000) * ms);
}

void delay_us(uint32_t us) {
    SysCtlDelay((g_ui32SysClock / 3000000) * us);
}

uint32_t hcsr04_read_cm(void) {
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, GPIO_PIN_2);
    delay_us(10);
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, 0);

    while(!GPIOPinRead(GPIO_PORTB_BASE, GPIO_PIN_3));

    uint32_t count = 0;
    while(GPIOPinRead(GPIO_PORTB_BASE, GPIO_PIN_3)) {
        count++;
    }

    float tiempo_us = count * 0.195;
    return tiempo_us / 58.0;
}

#define PWM_PERIOD 1000

char uart_buf[32];
uint8_t uart_idx = 0;
uint32_t g_speed = 50;

// DIRECCIÓN
void motor1_forward() { GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4); }
void motor1_backward(){ GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_5); }
void motor2_forward() { GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4); }
void motor2_backward(){ GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_5); }
void motores_stop() {
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);
}

int main(void) {

    g_ui32SysClock = SysCtlClockFreqSet(
        (SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
         SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240), 120000000);

    // UART
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOA));
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTConfigSetExpClk(UART0_BASE, g_ui32SysClock, 115200,
        (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));

    // Buzzer
    GPIOPinTypeGPIOOutput(GPIO_PORTA_BASE, GPIO_PIN_6);

    // PWM
    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    GPIOPinConfigure(GPIO_PF1_M0PWM1);
    GPIOPinConfigure(GPIO_PF2_M0PWM2);
    GPIOPinTypePWM(GPIO_PORTF_BASE, GPIO_PIN_1 | GPIO_PIN_2);

    PWMClockSet(PWM0_BASE, PWM_SYSCLK_DIV_64);
    PWMGenConfigure(PWM0_BASE, PWM_GEN_0, PWM_GEN_MODE_DOWN);
    PWMGenConfigure(PWM0_BASE, PWM_GEN_1, PWM_GEN_MODE_DOWN);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, PWM_PERIOD);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_1, PWM_PERIOD);

    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, PWM_PERIOD * 50 / 100);
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_2, PWM_PERIOD * 50 / 100);

    PWMOutputState(PWM0_BASE, PWM_OUT_1_BIT | PWM_OUT_2_BIT, true);
    PWMGenEnable(PWM0_BASE, PWM_GEN_0);
    PWMGenEnable(PWM0_BASE, PWM_GEN_1);

    // Pines motores
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOM);
    GPIOPinTypeGPIOOutput(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5);
    GPIOPinTypeGPIOOutput(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5);

    // Ultrasonico
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    GPIOPinTypeGPIOOutput(GPIO_PORTB_BASE, GPIO_PIN_2);
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, 0);
    GPIOPinTypeGPIOInput(GPIO_PORTB_BASE, GPIO_PIN_3);

    while(1) {

        uint32_t dist = hcsr04_read_cm();
        UARTSendString("dist:");
        UARTSendInt(dist);
        UARTSendString("\n");

        if (dist > 0 && dist <= 3) {
            motores_stop();
            UARTSendString("stop\n");
        }

        while(UARTCharsAvail(UART0_BASE)) {
            char c = UARTCharGet(UART0_BASE);

            if (c == '\n') {
                uart_buf[uart_idx] = '\0';

                if (uart_buf[0]=='f') {
                    motor1_forward();
                    motor2_forward();
                }
                else if (uart_buf[0]=='b' && uart_buf[1]=='a') {
                    motor1_backward();
                    motor2_backward();
                }
                else if (uart_buf[0]=='l') {
                    motor1_backward();
                    motor2_forward();
                }
                else if (uart_buf[0]=='r') {
                    motor1_forward();
                    motor2_backward();
                }
                else if (uart_buf[0]=='s' && uart_buf[1]=='t') {
                    motores_stop();
                }
                else if (uart_buf[0]=='b' && uart_buf[1]=='u') {
                    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, GPIO_PIN_6);
                    delay_ms(1000);
                    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, 0);
                }
                else if (uart_buf[0]=='s' && uart_buf[1]=='p') {

                    uint32_t spd = 0;
                    for (int i = 6; uart_buf[i] >= '0' && uart_buf[i] <= '9'; i++)
                        spd = spd * 10 + (uart_buf[i] - '0');

                    if (spd > 100) spd = 100;
                    g_speed = spd;

                    float f1 = 1.0;
                    float f2 = 0.92;

                    uint32_t d1 = PWM_PERIOD * g_speed * f1 / 100;
                    uint32_t d2 = PWM_PERIOD * g_speed * f2 / 100;

                    if (d1 > PWM_PERIOD) d1 = PWM_PERIOD;
                    if (d2 > PWM_PERIOD) d2 = PWM_PERIOD;

                    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, d1);
                    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_2, d2);
                }

                uart_idx = 0;
            }
            else if (uart_idx < 31) {
                uart_buf[uart_idx++] = c;
            }
        }

        delay_ms(50);
    }
}