#include <stdint.h>
#include <stdbool.h>
#include "inc/hw_memmap.h"
#include "driverlib/sysctl.h"
#include "driverlib/gpio.h"
#include "driverlib/uart.h"
#include "driverlib/pin_map.h"
#include "driverlib/pwm.h"


uint32_t reloj_sistema;     
#define PWM_PERIOD 1000     

char buffer_texto[32];      
uint8_t indice_texto = 0;   


// Función para mandar palabras
void mandar_palabra(const char *texto) {
    while (*texto) {
        UARTCharPut(UART0_BASE, *texto++); // Manda letra por letra
    }
}

// Función para mandar números (como la distancia)
void mandar_numero(uint32_t valor) {
    char texto_numero[12];
    int i = 0;
    if (valor == 0) {
        UARTCharPut(UART0_BASE, '0');
        return;
    }
    // Convertimos el número de matemáticas a texto para poder enviarlo
    while (valor > 0) {
        texto_numero[i++] = '0' + (valor % 10);
        valor /= 10;
    }
    for (int j = i-1; j >= 0; j--) {
        UARTCharPut(UART0_BASE, texto_numero[j]);
    }
}

// Un pequeño descanso en microsegundos
void pausa_us(uint32_t us) {
    SysCtlDelay((reloj_sistema / 3000000) * us);
}


//Ultrasonico
uint32_t medir_distancia_cm(void) {
    // 1. Damos el grito (Pin PB2 en ALTO)
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, GPIO_PIN_2);
    pausa_us(10);
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, 0); 

    uint32_t tiempo_espera = 0;
    
   
    while(!GPIOPinRead(GPIO_PORTB_BASE, GPIO_PIN_3)) {
        if(++tiempo_espera > 500000) return 999; 
    }

    uint32_t contador_tiempo = 0;
    while(GPIOPinRead(GPIO_PORTB_BASE, GPIO_PIN_3)) {
        contador_tiempo++;
        if(contador_tiempo > 500000) return 999;
    }

    // 4. Tiempo a centímetros
    return (contador_tiempo * 1500) / 1000000;
}





int main(void) {
    
    // 1. Encendemos la Tiva a 120 MHz 
    reloj_sistema = SysCtlClockFreqSet((SYSCTL_XTAL_25MHZ | SYSCTL_OSC_MAIN | SYSCTL_USE_PLL | SYSCTL_CFG_VCO_240), 120000000);

    // 2. Preparamos (UART0) para la Raspberry a 115200 baudios
    SysCtlPeripheralEnable(SYSCTL_PERIPH_UART0);
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOA);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOA));
    GPIOPinConfigure(GPIO_PA0_U0RX);
    GPIOPinConfigure(GPIO_PA1_U0TX);
    GPIOPinTypeUART(GPIO_PORTA_BASE, GPIO_PIN_0 | GPIO_PIN_1);
    UARTConfigSetExpClk(UART0_BASE, reloj_sistema, 115200, (UART_CONFIG_WLEN_8 | UART_CONFIG_STOP_ONE | UART_CONFIG_PAR_NONE));

    // 3.  motores PWM en PF1 y PF2
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
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, 0); // Arranca detenido
    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_2, 0); // Arranca detenido
    PWMOutputState(PWM0_BASE, PWM_OUT_1_BIT | PWM_OUT_2_BIT, true);
    PWMGenEnable(PWM0_BASE, PWM_GEN_0);
    PWMGenEnable(PWM0_BASE, PWM_GEN_1);





    // 4. dirección del Motor 1 (PE4 y PE5)
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOE);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOE));
    GPIOPinTypeGPIOOutput(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);

    // 5. dirección del Motor 2 (PM4 y PM5)
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOM);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOM));
    GPIOPinTypeGPIOOutput(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5);
    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0);



    // 6. Ultrasónico en PB2 y PB3
    SysCtlPeripheralEnable(SYSCTL_PERIPH_GPIOB);
    while(!SysCtlPeripheralReady(SYSCTL_PERIPH_GPIOB));
    GPIOPinTypeGPIOOutput(GPIO_PORTB_BASE, GPIO_PIN_2); // TRIG
    GPIOPinWrite(GPIO_PORTB_BASE, GPIO_PIN_2, 0);
    GPIOPinTypeGPIOInput(GPIO_PORTB_BASE, GPIO_PIN_3);  // ECHO
    GPIOPadConfigSet(GPIO_PORTB_BASE, GPIO_PIN_3, GPIO_STRENGTH_2MA, GPIO_PIN_TYPE_STD_WPD);

    
    while(1) {
        
        // 1 Medir y mandar a la Raspi
        uint32_t distancia = medir_distancia_cm();
        mandar_palabra("dist:");
        mandar_numero(distancia);
        mandar_palabra("\n");

        // 2  si la Raspberry nos manda alguna tecla
        while(UARTCharsAvail(UART0_BASE)) {
            char letra_recibida = UARTCharGet(UART0_BASE);
            
            // Si la Raspberry presiona y termina
            if (letra_recibida == '\n') {
                buffer_texto[indice_texto] = '\0'; // Cerramos la palabra
                
               
                
                // 'w' (Adelante)
                if (buffer_texto[0] == 'w') {
                    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4); // Motor 1 adelante
                    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4); // Motor 2 adelante
                } 
                // 's' (Atrás)
                else if (buffer_texto[0] == 's') {
                    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_5); // Motor 1 atras
                    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_5); // Motor 2 atras
                } 
                // 'a' (Izquierda)
                else if (buffer_texto[0] == 'a') {
                    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_5); // Motor 1 atras
                    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4); // Motor 2 adelante
                } 
                // 'd' (Derecha)
                else if (buffer_texto[0] == 'd') {
                    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_4); // Motor 1 adelante
                    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, GPIO_PIN_5); // Motor 2 atras
                } 
                // 'x' (Freno)
                else if (buffer_texto[0] == 'x') {
                    GPIOPinWrite(GPIO_PORTE_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0); 
                    GPIOPinWrite(GPIO_PORTM_BASE, GPIO_PIN_4 | GPIO_PIN_5, 0); 
                } 
                // Si mandó un cambio de velocidad (ej. "speed:100")
                else if (buffer_texto[0] == 's' && buffer_texto[1] == 'p') {
                    uint32_t nueva_velocidad = 0;
                    // Leemos el número que nos pasó
                    for (int i = 6; buffer_texto[i] >= '0' && buffer_texto[i] <= '9'; i++) {
                        nueva_velocidad = nueva_velocidad * 10 + (buffer_texto[i] - '0');
                    }
                    if (nueva_velocidad > 100) nueva_velocidad = 100;
                    
                    // Aplicamos la velocidad a los PWM
                    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_1, PWM_PERIOD * nueva_velocidad / 100);
                    PWMPulseWidthSet(PWM0_BASE, PWM_OUT_2, PWM_PERIOD * nueva_velocidad / 100);
                }
                
                indice_texto = 0; 
            } 
            else if (indice_texto < 31) {
             
                buffer_texto[indice_texto++] = letra_recibida;
            }
        }
        

        SysCtlDelay(reloj_sistema / 300); 
    }
}