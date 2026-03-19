#******************************************************************************
#
# Makefile - Rules for building the lab4ej3 example.
#
#******************************************************************************

# Define el tipo de parte que utiliza este proyecto.
PART=TM4C1294NCPDT

# El directorio base para TivaWare (Ajusta si es necesario).
ROOT=../../../..

# Incluye las definiciones comunes de make.
include ${ROOT}/makedefs

# Ruta para encontrar archivos de cabecera.
IPATH=../../../..

# Regla por defecto para construir el proyecto.
all: ${COMPILER}
all: ${COMPILER}/lab4ej3.axf

# Regla para limpiar los productos de la compilación.
clean:
	@rm -rf ${COMPILER} ${wildcard *~}

# Regla para crear el directorio de destino (gcc).
${COMPILER}:
	@mkdir -p ${COMPILER}

# Reglas para construir el ejecutable .axf
${COMPILER}/lab4ej3.axf: ${COMPILER}/lab4ej3.o
${COMPILER}/lab4ej3.axf: ${COMPILER}/startup_${COMPILER}.o
${COMPILER}/lab4ej3.axf: ${ROOT}/driverlib/${COMPILER}/libdriver.a
${COMPILER}/lab4ej3.axf: lab4ej3.ld

# Configuración del Linker y Compilador
SCATTERgcc_lab4ej3=lab4ej3.ld
ENTRY_lab4ej3=ResetISR

# ESTA ES LA LÍNEA CLAVE QUE CORRIGE EL ERROR DE OVERLAP
CFLAGSgcc=-DTARGET_IS_TM4C129_RA1 -fno-unwind-tables -fno-asynchronous-unwind-tables

# Incluir archivos de dependencia generados automáticamente.
ifneq (${MAKECMDGOALS},clean)
-include ${wildcard ${COMPILER}/*.d} __dummy__
endif
