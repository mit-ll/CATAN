CC=gcc
CFLAGS=-Wall
OBJ = broadcast_bridge.o 

%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

broadcast_bridge: $(OBJ)
	gcc -o $@ $^ $(CFLAGS)

