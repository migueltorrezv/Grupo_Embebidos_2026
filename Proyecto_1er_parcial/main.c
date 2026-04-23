#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/uart.h"
#include "driverlib/pin_map.h"
#include "inc/hw_types.h"

/*
 * Raspberry Pi envia por UART:
 *   "red\n"   → color rojo detectado
 *   "green\n" → color verde detectado
 *   "blue\n"  → color azul detectado
 *   "none\n"  → ningún color detectado
 *
 * Conexión física:
 *   Raspberry Pi TX (GPIO14) → TIVA PA0 (U0RX)
 *   Raspberry Pi RX (GPIO15) → TIVA PA1 (U0TX)
 *   GND compartido
 *
 * LEDs de confirmación (puedes cambiar los pines):
 *   Rojo   → PN0
 *   Verde  → PN1
 *   Azul   → PF0
 */

uint32_t g_ui32SysClock;

/* ── UART helpers ─────────────────────────────────────────── */
void UARTSendString(const char *str) {
    while (*str) UARTCharPut(UART0_BASE, *str++);
}

/* ── Delay ────────────────────────────────────────────────── */
void delay_ms(uint32_t ms) {
    SysCtlDelay((g_ui32SysClock / 3000) * ms);
}

/* ── Buffer UART ──────────────────────────────────────────── */
char uart_buf[32];
uint8_t uart_idx = 0;

int str_cmp(const char *a, const char *b) {
    while (*a && *b) { if (*a != *b) return 0; a++; b++; }
    return *a == *b;
}

/* ── Acciones por color ───────────────────────────────────── */
void on_red(void) {
    UARTSendString("color:red\n");
    /* Encender LED rojo en PN0 */
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0, GPIO_PIN_0);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, 0);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, 0);
    /* Agrega aquí lo que quieras hacer al detectar rojo */
}

void on_green(void) {
    UARTSendString("color:green\n");
    /* Encender LED verde en PN1 */
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0, 0);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, GPIO_PIN_1);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, 0);
    /* Agrega aquí lo que quieras hacer al detectar verde */
}

void on_blue(void) {
    UARTSendString("color:blue\n");
    /* Encender LED azul en PF0 */
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0, 0);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_1, 0);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, GPIO_PIN_0);
    /* Agrega aquí lo que quieras hacer al detectar azul */
}

void on_none(void) {
    UARTSendString("color:none\n");
    /* Apagar todos los LEDs */
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, 0);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, 0);
}

/* ── Main ─────────────────────────────────────────────────── */
int main(void) {
    g_ui32SysClock = SysCtlClockFreqSet(
        (SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN |
         SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240), 120000000);

    /* UART0 — PA0 (RX), PA1 (TX) — igual que tu ejemplo */
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOA));
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTConfigSetExpClk(UART0_BASE, g_ui32SysClock, 115200,
        (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));

    /* LEDs de confirmación — PN0, PN1 */
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPION);
    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_GPION));
    GPIOPinTypeGPIOOutput(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    GPIOPinWrite(GPIO_PORTN_BASE, GPIO_PIN_0 | GPIO_PIN_1, 0);

    /* LED azul — PF0 */
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOF);
    while (!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOF));
    GPIOPinTypeGPIOOutput(GPIO_PORTF_BASE, GPIO_PIN_0);
    GPIOPinWrite(GPIO_PORTF_BASE, GPIO_PIN_0, 0);

    UARTSendString("TIVA lista. Esperando colores...\n");

    while (1) {
        /* Leer UART byte a byte hasta '\n' */
        while (UARTCharsAvail(UART0_BASE)) {
            char c = UARTCharGet(UART0_BASE);

            if (c == '\n') {
                uart_buf[uart_idx] = '\0';

                if      (str_cmp(uart_buf, "red"))   on_red();
                else if (str_cmp(uart_buf, "green")) on_green();
                else if (str_cmp(uart_buf, "blue"))  on_blue();
                else if (str_cmp(uart_buf, "none"))  on_none();
                else {
                    UARTSendString("cmd_desconocido:");
                    UARTSendString(uart_buf);
                    UARTSendString("\n");
                }

                uart_idx = 0;
            } else if (uart_idx < 31) {
                uart_buf[uart_idx++] = c;
            }
        }

        delay_ms(10);
    }
}
