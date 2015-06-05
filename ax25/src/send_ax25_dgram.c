// © 2015 Massachusetts Institute of Technology

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 
#include <errno.h>
#include <math.h>
#include <netax25/ax25.h>
#include <netax25/axlib.h>
#include <netax25/axconfig.h>

#define BUFSIZE 512
#define HEADSIZE 5

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

int send_ax25_dgram(char* port, 
		    char* dest_call, 
		    char* message) 
{
    struct full_sockaddr_ax25 serv_addr;
    struct full_sockaddr_ax25 cli_addr;
    int addrlen = sizeof(struct full_sockaddr_ax25);

    //need to call ax25_config_load_ports() before any other config calls
    if (ax25_config_load_ports() == 0) {
	error("ERROR loading axports file");
    }
    //get our own call sign assigned to the port
    char* src_call = ax25_config_get_addr(port);
    if (src_call == NULL) {
	error("Could not find address on specified port");
    }
    //get the AX25 packet length set in /etc/ax25/axports
    int paclen = ax25_config_get_paclen(port);

    fprintf(stdout, "   %s calling %s... ", src_call, dest_call);
    fflush(stdout);

    //specify the callsign to which we want to send
    bzero((char *) &serv_addr, sizeof(serv_addr));
    ax25_aton(dest_call, &serv_addr);
    
    //specify our callsign 
    bzero((char *) &cli_addr, sizeof(cli_addr));
    ax25_aton(src_call, &cli_addr);

    //create the AX25 socket
    //int sockfd = socket(AF_AX25, SOCK_DGRAM, 0);
    int sockfd = socket(AF_AX25, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        error("ERROR opening socket");
    }

    if (bind(sockfd, (struct sockaddr *) &cli_addr, sizeof(cli_addr)) < 0) {
    	error("ERROR on binding");
    }

    size_t bytes = strlen(message);

    printf( "message = %s... ", message);
    int sent = sendto(sockfd, message, bytes, 0,
		      (struct sockaddr *) &serv_addr, sizeof(serv_addr));
    if (sent < 0) {
	error("Error on send");
    }

    close(sockfd);
    printf("done\n");
    return 0;
}


int main(int argc, char *argv[])
{
    //char* port = "radio";

    if (argc < 4) {
       fprintf(stderr,"usage %s <port> <dest_callsign> <message>\n", argv[0]);
       exit(1);
    }

    char *port = argv[1];
    char *dest_call = argv[2];
    char *message = argv[3];

    int result = send_ax25_dgram(port, dest_call, message);

    return result;
}
