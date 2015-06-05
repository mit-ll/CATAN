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
#define HEADSIZE 5  //must match HEADFORMAT
#define HEADFORMAT "%05u"

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

int send_ax25_packet(char* port, char* dest_call, char* message) 
{
    struct full_sockaddr_ax25 sockaddr;
    int addrlen = sizeof(struct full_sockaddr_ax25);

    //create the AX25 socket
    int sockfd = socket(AF_AX25, SOCK_SEQPACKET, 0);
    if (sockfd < 0) {
        error("ERROR opening socket");
    }

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

    //specify the callsign to which we want to connect
    bzero((char *) &sockaddr, sizeof(sockaddr));
    ax25_aton(dest_call, &sockaddr);
 
    //connect to the specified address, keep trying if busy
    int status;
    while (status = connect(sockfd,(struct sockaddr *) &sockaddr, sizeof(sockaddr)) < 0){
	fprintf(stdout, " busy, waiting to connect...");
        fflush(stdout);
        sleep(2);    
    }
    printf(" connected... ");
    //printf("Sending %u byte message: %s...", (unsigned int) strlen(message), message);
    fflush(stdout);

    //generate header: the length of data in bytes is encoded as
    //                 a decimal number with HEADSIZE ASCII chars 
    size_t bytes = strlen(message);
    int max_msg_size = (int) (pow(10, HEADSIZE)-1);
    if (bytes < max_msg_size) {
        char header[HEADSIZE+1];
        snprintf(header, HEADSIZE+1, HEADFORMAT, (unsigned int) bytes); 
        int head_written = write(sockfd, header, strlen(header));
        //printf(" header: %s ", header); 
    } else {
	error("Message to long");
    }

    //fragment packet if necessary
    int offset = 0;
    while (offset != bytes) {
	int len = (bytes - offset > paclen) ? paclen : bytes - offset;
        int written = write(sockfd, message+offset, len);
	//printf(" %d bytes written...", written);
        if (written == 0) {
            printf(" no data written... ");
	    break;
        }
        if (written == -1) {
	    error("Error on write");
	}
	offset += written;
    }

    printf(" data sent... ");
    fflush(stdout);
    
    char read_buf[HEADSIZE+1];
    bzero(read_buf,HEADSIZE+1);
    int read_cnt = read(sockfd,read_buf,HEADSIZE);  //Could block a while
    if (read_cnt < 0) {
         error("ERROR reading from socket in client");
    }

    //test that the response shows the correct number of bytes were received
    if (bytes != atoi(read_buf) ) {
	error("ERROR: Data transfer incomplete");
    }

    //printf("%s...",read_buf);
    printf("response received... ");
    fflush(stdout);  

    close(sockfd);
    printf("connection closed\n");
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

    int result = send_ax25_packet(port, dest_call, message);

    return result;
}



