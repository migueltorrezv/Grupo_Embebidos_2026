
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
    uint32_t timeout = 0;
    while(!GPIOPinRead(GPIO_PORTB_BASE, GPIO_PIN_3)) {
        if(++timeout > 500000) return 999;
    }
    uint32_t count = 0;
    while(GPIOPinRead(GPIO_PORTB_BASE, GPIO_PIN_3)) {
        count++;
        if(count > 500000) return 999;
    }
    float tiempo_us = count * 0.195;
    return (uint32_t)(tiempo_us / 58.0);
}

#define PWM_PERIOD 1000
uint32_t g_speed = 50;

void set_pwm(uint32_t spd) {
    float f1 = 1.9, f2 = 1.5;
    uint32_t d1 = (uint32_t)(PWM_PERIOD * spd * f1 / 100.0);
    uint32_t d2 = (uint32_t)(PWM_PERIOD * spd * f2 / 100.0);
    if (d1 > PWM_PERIOD) d1 = PWM_PERIOD;
    if (d2 > PWM_PERIOD) d2 = PWM_PERIOD;
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, d1);
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_2, d2);
}

void motor_forward(void) {
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_4);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_4);
    UARTSendString("moving:forward\n");
}

void motor_backward(void) {
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_5);
    UARTSendString("moving:backward\n");
}

void motor_left(void) {
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_4);
    UARTSendString("moving:left\n");
}

void motor_right(void) {
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_4);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4|GPIO_PIN_5, GPIO_PIN_5);
    UARTSendString("moving:right\n");
}

void motor_stop(void) {
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4|GPIO_PIN_5, 0);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4|GPIO_PIN_5, 0);
    UARTSendString("moving:stop\n");
}

void motor_rotate180(void) {
    motor_right();
    delay_ms(1000);
    motor_stop();
}

char uart_buf[32];
uint8_t uart_idx = 0;
uint8_t modo = 1;

int cmp(const char *a, const char *b) {
    while (*a && *b) { if (*a != *b) return 0; a++; b++; }
    return *a == *b;
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
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0|GPIO_PIN_1);
    UARTConfigSetExpClk(UART0_BASE, g_ui32SysClock, 115200,
                        (UART_CONFIG_WLEN_8|UART_CONFIG_STOP_ONE|UART_CONFIG_PAR_NONE));

    GPIOPinTypeGPIOOutput(GPIO_PORTA_BASE, GPIO_PIN_6);
    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, 0);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOJ);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOJ));
    GPIOPinTypeGPIOInput(GPIO_PORTJ_BASE, GPIO_PIN_0|GPIO_PIN_1);
    GPIOPadConfigSet(GPIO_PORTJ_BASE, GPIO_PIN_0|GPIO_PIN_1,
                     GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPU);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_PWM0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    GPIOPinConfigure(GPIO_PF1_M0PWM1);
    GPIOPinConfigure(GPIO_PF2_M0PWM2);
    GPIOPinTypePWM(GPIO_PORTF_BASE, GPIO_PIN_1|GPIO_PIN_2);
    PWMClockSet(PWM0_BASE, PWM_SYSCLK_DIV_64);
    PWMGenConfigure(PWM0_BASE, PWM_GEN_0, PWM_GEN_MODE_DOWN|PWM_GEN_MODE_NO_SYNC);
    PWMGenConfigure(PWM0_BASE, PWM_GEN_1, PWM_GEN_MODE_DOWN|PWM_GEN_MODE_NO_SYNC);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_0, PWM_PERIOD);
    PWMGenPeriodSet(PWM0_BASE, PWM_GEN_1, PWM_PERIOD);
    set_pwm(50);
    PWMOutputState(PWM0_BASE, PWM_OUT_1_BIT|PWM_OUT_2_BIT, true);
    PWMGenEnable(PWM0_BASE, PWM_GEN_0);
    PWMGenEnable(PWM0_BASE, PWM_GEN_1);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOE));
    GPIOPinTypeGPIOOutput(GPIO_PORTE_BASE, GPIO_PIN_4|GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4|GPIO_PIN_5, 0);

    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOM);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOM));
    GPIOPinTypeGPIOOutput(GPIO_PORTM_BASE, GPIO_PIN_4|GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4|GPIO_PIN_5, 0);

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
        if (!sw1 && sw1_prev) { modo = 1; motor_forward(); }
        if (!sw2 && sw2_prev) { modo = 0; motor_stop(); }
        sw1_prev = sw1;
        sw2_prev = sw2;

        if (modo == 1) {
            uint32_t dist = hcsr04_read_cm();
            UARTSendString("dist:");
            UARTSendInt(dist);
            UARTSendString("\n");
            if (dist > 0 && dist <= 5) {
                motor_stop();
                delay_ms(500);
                motor_rotate180();
                delay_ms(200);
                motor_forward();
                UARTSendString("obstacle\n");
            }
        }

        while(UARTCharsAvail(UART0_BASE)) {
            char c = UARTCharGet(UART0_BASE);
            if (c == '\n') {
                uart_buf[uart_idx] = '\0';
                if      (cmp(uart_buf, "forward"))   { modo = 0; motor_forward(); }
                else if (cmp(uart_buf, "backward"))  { modo = 0; motor_backward(); }
                else if (cmp(uart_buf, "left"))      { modo = 0; motor_left(); }
                else if (cmp(uart_buf, "right"))     { modo = 0; motor_right(); }
                else if (cmp(uart_buf, "stop"))      { modo = 0; motor_stop(); }
                else if (cmp(uart_buf, "auto"))      { modo = 1; motor_forward(); }
                else if (cmp(uart_buf, "rotate180")) { motor_rotate180(); motor_forward(); }
                else if (cmp(uart_buf, "buzzer")) {
                    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, GPIO_PIN_6);
                    delay_ms(2000);
                    GPIOPinWrite(GPIO_PORTA_BASE, GPIO_PIN_6, 0);
                }
                else if (uart_buf[0]=='s' && uart_buf[1]=='p' &&
                    uart_buf[2]=='e' && uart_buf[3]=='e' &&
                    uart_buf[4]=='d' && uart_buf[5]==':') {
                    uint32_t spd = 0;
                for (int i = 6; uart_buf[i] >= '0' && uart_buf[i] <= '9'; i++)
                    spd = spd * 10 + (uart_buf[i] - '0');
                    if (spd > 100) spd = 100;
                    g_speed = spd;
                    set_pwm(g_speed);
                    }
                    uart_idx = 0;
            } else if (uart_idx < 31) {
                uart_buf[uart_idx++] = c;
            }
        }

        delay_ms(50);
    }
}
