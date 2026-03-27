TIVAWARE = /home/angel/TivaWare

CC      = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy

CFLAGS  = -mthumb -mcpu=cortex-m4 -mfpu=fpv4-sp-d16 -mfloat-abi=hard
CFLAGS += -Os -ffunction-sections -fdata-sections
CFLAGS += -I$(TIVAWARE)
CFLAGS += -DPART_TM4C1294NCPDT -DTARGET_IS_TM4C129_RA2

LDFLAGS = -T tiva.ld -Wl,--gc-sections
LDFLAGS += -L$(TIVAWARE)/driverlib/gcc -ldriver
LDFLAGS += --specs=nosys.specs

SRC = ej2_uart_leds_tiva.c
BIN = $(SRC:.c=.bin)
AXF = $(SRC:.c=.axf)

all: $(BIN)

$(AXF): $(SRC)
	$(CC) $(CFLAGS) $(SRC) $(LDFLAGS) -o $(AXF)

$(BIN): $(AXF)
	$(OBJCOPY) -O binary $(AXF) $(BIN)

flash: $(BIN)
	lm4flash $(BIN)

clean:
	rm -f *.axf *.bin
