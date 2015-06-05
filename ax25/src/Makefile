CC=gcc
CFLAGS=-c 
LDLIBS=-lax25
EXES=send_packet_connected handler_ax25d send_ax25_dgram server_ax25_dgram send_unix_dgram recv_unix_dgram
TEMP=

all: $(EXES)
	rm *.o

clean:
	rm -f $(EXES) $(TEMP) *.o *~ 

send_packet_connected: send_packet_connected.o
	$(CC) $< $(LDLIBS) -o $@
send_packet_connected.o: send_packet_connected.c
	$(CC) $(CFLAGS) $< -o $@

handler_ax25d: handler_ax25d.o
	$(CC) $< $(LDLIBS) -o $@
handler_ax25d.o: handler_ax25d.c
	$(CC) $(CFLAGS) $< -o $@

send_ax25_dgram: send_ax25_dgram.o
	$(CC) $< $(LDLIBS) -o $@
send_ax25_dgram.o: send_ax25_dgram.c

server_ax25_dgram: server_ax25_dgram.o
	$(CC) $< $(LDLIBS) -o $@
server_ax25_dgram.o: server_ax25_dgram.c

send_unix_dgram: send_unix_dgram.o
	$(CC) $< $(LDLIBS) -o $@
send_unix_dgram.o: send_unix_dgram.c

recv_unix_dgram: recv_unix_dgram.o
	$(CC) $< $(LDLIBS) -o $@
recv_unix_dgram.o: recv_unix_dgram.c

