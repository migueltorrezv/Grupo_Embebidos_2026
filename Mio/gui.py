import serial
import time           
import threading       # dos cosas al mismo tiempo
import sys            
import termios         # teclado
import tty             # No lag en teclas

try:
    s = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
except:
    print("Error: Conecta la Tiva C al USB")
    sys.exit()



velocidad_actual = 70           
nitro_encendido = False         
robot_encendido = True          
freno_emergencia = False        
ultima_distancia = 999.0

# FUNCION 1: PREPARAR EL ROBOT
def preparar_pines():
    s.write(f"speed:{velocidad_actual}\n".encode())

# FUNCION 2: LECTOR SERIAL DE DISTANCIA 
def lector_serial():
    global ultima_distancia, robot_encendido
    while robot_encendido:
        if s.in_waiting:
            msg = s.readline().decode('utf-8', errors='ignore').strip()
            if msg.startswith("dist:"):
                try:
                    ultima_distancia = float(msg.split(":")[1])
                except:
                    pass
        time.sleep(0.01)

# FUNCION 3: MOVER LAS RUEDAS
def mover_robot(comando):
    global freno_emergencia
    
    if freno_emergencia == True:
        return 
        
    s.write(f"{comando}\n".encode())

def frenar_robot():
    s.write(b"x\n")

# FUNCION 4: NITRO (Punto 4)
def boton_nitro():
    global nitro_encendido, velocidad_actual
    
    # Cambia estado
    if nitro_encendido == True:
        nitro_encendido = False
        velocidad_actual = 70      # Velocidad normal
        print("\n[!] NITRO APAGADO: Volvemos a la programacion habitual de 70%")
    else:
        nitro_encendido = True
        velocidad_actual = 100     # Velocidad máxima
        print("\n[!] NITRO ENCENDIDO: ¡Agarrate los calzones que vamos al 100%!")
        
    s.write(f"speed:{velocidad_actual}\n".encode())

# FUNCION 5: TECLADO
def leer_tecla_al_instante():
    # Este es un truco para que no tengas que presionar 'Enter' cada vez que tocas direcciones 'W'
    # Lee directamente la memoria de tu teclado en tiempo real.
    configuracion_vieja = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        letra = sys.stdin.read(1)                        # Mantiene una sola letra
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, configuracion_vieja)
    
    return letra.lower() # Ignora la mayuscula

# FUNCION 6: STOP
def vigilante_de_choques():
    global robot_encendido, freno_emergencia, ultima_distancia
    
    while robot_encendido == True:
        # 10 cm por si no alcanza a parar
        if ultima_distancia < 10.0 and ultima_distancia > 0:
            
            # Frenada de emergencia
            if freno_emergencia == False:
                print("\n Parale jueputa")
                frenar_robot()
                freno_emergencia = True 
                
        # todo chill
        else:
            freno_emergencia = False 
        time.sleep(0.1) # descansito

# FUNCION PRINCIPAL: 
def iniciar_modelo_b():
    global robot_encendido
    preparar_pines()
    print("\n Modo B: TECLADO")
    print(" W: Adelante, S: Atras, A: Izquierda, D: Derecha")
    print("Nitro con: N  |  Parar con: X  |  Salir con: Q")
    
    # vigila adelante (Serial)
    trabajador_serial = threading.Thread(target=lector_serial)
    trabajador_serial.start()
    
    # vigila adelante (Logica)
    trabajador_vigilante = threading.Thread(target=vigilante_de_choques)
    trabajador_vigilante.start() 

    try:
        # Bucle de manejo
        while robot_encendido == True:
            tecla_tocada = leer_tecla_al_instante()
            
            # Adelante
            if tecla_tocada == 'w':
                mover_robot('w')
                
            # Atras
            elif tecla_tocada == 's':
                mover_robot('s')
                
            # Izquierda
            elif tecla_tocada == 'a':
                mover_robot('a')
                
            # Derecha
            elif tecla_tocada == 'd':
                mover_robot('d')
                
            # Nitro
            elif tecla_tocada == 'n':
                boton_nitro()
                
            # Freno manual
            elif tecla_tocada == 'x':
                frenar_robot()
                
            # Salir del juego
            elif tecla_tocada == 'q':
                robot_encendido = False
                frenar_robot()
                print("\n Hasta la vista baby")
                break
                
    finally:
        robot_encendido = False
        trabajador_vigilante.join()
        trabajador_serial.join()
        s.close()

if __name__ == "__main__":
    iniciar_modelo_b()