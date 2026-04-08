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

    // FACTOR CALIBRADO (ajústalo)
    float tiempo_us = count * 0.195;  // <-- AJUSTA ESTE VALOR
    return tiempo_us / 58.0;
}

#define PWM_PERIOD 1000

char uart_buf[32];
uint8_t uart_idx = 0;
uint32_t g_speed = 50;
bool motor1_on = false;
bool motor2_on = false;

void motor1_set(bool on) {
    motor1_on = on;
    if (on) GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4);
    else GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);
}

void motor2_set(bool on) {
    motor2_on = on;
    if (on) GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4);
    else GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);
}

int main(void) {
    g_ui32SysClock = SysCtlClockFreqSet(
        (SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
         SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240), 120000000);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOA));
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTConfigSetExpClk(UART0_BASE, g_ui32SysClock, 115200,
        (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));

    GPIOPinTypeGPIOOutput(GPIO_PORTA_BASE, GPIO_PIN_6);
    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, 0);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0 | GPIO_PIN_1,
        GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    GPIOPinConfigure(GPIO_PF1_M0PWM1);
    GPIOPinConfigure(GPIO_PF2_M0PWM2);
    GPIOPinTypePWM(GPIO_PORTF_BASE, GPIO_PIN_1 | GPIO_PIN_2);
    PWMClockSet(PWM0_BASE, PWM_SYSCLK_DIV_64);
    PWMGenConfigure(PWM0_BASE, PWM_GEN_0, PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);
    PWMGenConfigure(PWM0_BASE, PWM_GEN_1, PWM_GEN_MODE_DOWN | PWM_GEN_MODE_NO_SYNC);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, PWM_PERIOD);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_1, PWM_PERIOD);
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, PWM_PERIOD * 50 / 100);
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_2, PWM_PERIOD * 50 / 100);
    PWMOutputState(PWM0_BASE, PWM_OUT_1_BIT | PWM_OUT_2_BIT, true);
    PWMGenEnable(PWM0_BASE, PWM_GEN_0);
    PWMGenEnable(PWM0_BASE, PWM_GEN_1);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOE));
    GPIOPinTypeGPIOOutput(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOM);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOM));
    GPIOPinTypeGPIOOutput(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOB));
    GPIOPinTypeGPIOOutput(GPIO_PORTB_BASE, GPIO_PIN_2);
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, 0);
    GPIOPinTypeGPIOInput(GPIO_PORTB_BASE, GPIO_PIN_3);
    GPIOPadConfigSet(GPIO_PORTB_BASE, GPIO_PIN_3, GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPD);

    bool sw1_prev = true, sw2_prev = true;

    while(1) {
        bool sw1 = GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_0);
        bool sw2 = GPIOPinRead(GPIO_PORTJ_BASE, GPIO_PIN_1);

        if (!sw1 && sw1_prev) {
            motor1_set(!motor1_on);
            UARTSendString(motor1_on ? "motor1:on\n" : "motor1:off\n");
        }
        if (!sw2 && sw2_prev) {
            motor2_set(!motor2_on);
            UARTSendString(motor2_on ? "motor2:on\n" : "motor2:off\n");
        }
        sw1_prev = sw1;
        sw2_prev = sw2;

        uint32_t dist = hcsr04_read_cm();
        UARTSendString("dist:");
        UARTSendInt(dist);
        UARTSendString("\n");
        if (dist > 0 && dist <= 3) {
            motor1_set(false);
            motor2_set(false);
            UARTSendString("stop\n");
        }

        while(UARTCharsAvail(UART0_BASE)) {
            char c = UARTCharGet(UART0_BASE);
            if (c == '\n') {
                uart_buf[uart_idx] = '\0';
                // buzzer
                if (uart_buf[0]=='b' && uart_buf[1]=='u' &&
                    uart_buf[2]=='z' && uart_buf[3]=='z' &&
                    uart_buf[4]=='e' && uart_buf[5]=='r') {
                    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, GPIO_PIN_6);
                    delay_ms(2000);
                    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, 0);
                }
                // motor1
                if (uart_buf[0]=='m' && uart_buf[1]=='o' &&
                    uart_buf[2]=='t' && uart_buf[3]=='o' &&
                    uart_buf[4]=='r' && uart_buf[5]=='1') {
                    motor1_set(!motor1_on);
                    UARTSendString(motor1_on ? "motor1:on\n" : "motor1:off\n");
                }
                // motor2
                if (uart_buf[0]=='m' && uart_buf[1]=='o' &&
                    uart_buf[2]=='t' && uart_buf[3]=='o' &&
                    uart_buf[4]=='r' && uart_buf[5]=='2') {
                    motor2_set(!motor2_on);
                    UARTSendString(motor2_on ? "motor2:on\n" : "motor2:off\n");
                }
                // speed
                if (uart_buf[0]=='s' && uart_buf[1]=='p' &&
                    uart_buf[2]=='e' && uart_buf[3]=='e' &&
                    uart_buf[4]=='d' && uart_buf[5]==':') {
                    uint32_t spd = 0;
                    for (int i = 6; uart_buf[i] >= '0' && uart_buf[i] <= '9'; i++)
                        spd = spd * 10 + (uart_buf[i] - '0');
                    if (spd > 100) spd = 100;
                    g_speed = spd;
                    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, PWM_PERIOD * g_speed / 100);
                    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_2, PWM_PERIOD * g_speed / 100);
                }
                uart_idx = 0;
            } else if (uart_idx < 31) {
                uart_buf[uart_idx++] = c;
            }
        }

        delay_ms(100);
    }
}
