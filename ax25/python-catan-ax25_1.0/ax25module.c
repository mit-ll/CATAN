// © 2015 Massachusetts Institute of Technology

#include <Python.h>
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

//return 0 for success, 1 for error
void error(const char *msg)
{
    perror(msg);
    //exit(1);
}

int init_ports(void) {
    //need to call ax25_config_load_ports() before any other config calls
    if (ax25_config_load_ports() == 0) {
	error("ERROR loading axports file");
	return 1;
    }
    return 0;
}

int send_ax25_dgram(char* port, 
		    char* dest_call, 
		    char* message,
                    int message_size) 
{
    struct full_sockaddr_ax25 serv_addr;
    struct full_sockaddr_ax25 cli_addr;

    //call to ax25_config_load_ports() done during module initialization

    //get our own call sign assigned to the port
    char* src_call = ax25_config_get_addr(port);
    if (src_call == NULL) {
	error("Could not find address on specified port");
	return 1;
    }
    //get the AX25 packet length set in /etc/ax25/axports
    int paclen = ax25_config_get_paclen(port);
    if (message_size > paclen) {
	error("Message exceeds maximum packet length");
	return 1;
    }

    //fprintf(stdout, "   %s calling %s... ", src_call, dest_call);
    //fflush(stdout);

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
	return 1;
    }

    if (bind(sockfd, (struct sockaddr *) &cli_addr, sizeof(cli_addr)) < 0) {
    	error("ERROR on binding");
	return 1;
    }

    //size_t bytes = strlen(message);  //Causes problem if buffers has null bytes

    //printf( "send_dgram: message = %s... ", message);
    int sent = sendto(sockfd, message, message_size, 0,
		      (struct sockaddr *) &serv_addr, sizeof(serv_addr));
    if (sent < 0) {
	error("Error on send");
	return 1;
    }

    close(sockfd);
    //printf("done\n");
    return 0;
}

int send_ax25_packet(char* port, 
		     char* dest_call, 
                     char* message) 
{
    struct full_sockaddr_ax25 sockaddr;

    //create the AX25 socket
    int sockfd = socket(AF_AX25, SOCK_SEQPACKET, 0);
    if (sockfd < 0) {
        error("ERROR opening socket");
	return 1;
    }

    //call to ax25_config_load_ports() done during module initialization

    //get our own call sign assigned to the port
    char* src_call = ax25_config_get_addr(port);
    if (src_call == NULL) {
	error("Could not find address on specified port");
	return 1;
    }
    //get the AX25 packet length set in /etc/ax25/axports
    int paclen = ax25_config_get_paclen(port);

    //fprintf(stdout, "   %s calling %s... ", src_call, dest_call);
    //fflush(stdout);

    //specify the callsign to which we want to connect
    bzero((char *) &sockaddr, sizeof(sockaddr));
    ax25_aton(dest_call, &sockaddr);
 
    //connect to the specified address, keep trying if busy
    int number_of_tries = 10;
    while (connect(sockfd,(struct sockaddr *) &sockaddr, sizeof(sockaddr)) < 0){
	fprintf(stdout, " busy, waiting to connect...");
        fflush(stdout);
        if (number_of_tries-- < 0) {
	    close(sockfd);
	    return 1;
	}

        sleep(2);
    }
    //printf(" connected... ");
    //printf("Sending %u byte message: %s...", (unsigned int) strlen(message), message);
    //fflush(stdout);

    //generate header: the length of data in bytes is encoded as
    //                 a decimal number with HEADSIZE ASCII chars 
    size_t bytes = strlen(message);
    int max_msg_size = (int) (pow(10, HEADSIZE)-1);
    if (bytes < max_msg_size) {
        char header[HEADSIZE+1];  
        snprintf(header, HEADSIZE+1, HEADFORMAT, (unsigned int) bytes); 
        int head_written = write(sockfd, header, strlen(header));
        if (head_written != strlen(header)) {
            printf("Header bytes written = %d\n", head_written);
            error("Incomplete header written");
	    return 1;
	}
        //printf(" header: %s ", header); 
    } else {
	error("Message to long");
	return 1;
    }

    //fragment packet if necessary
    int offset = 0;
    while (offset != bytes) {
	int len = (bytes - offset > paclen) ? paclen : bytes - offset;
        int written = write(sockfd, message+offset, len);
	//printf(" %d bytes written...", written);
        if (written == 0) {
            //printf(" no data written... ");
	    break;
        }
        if (written == -1) {
	    error("Error on write");
	    return 1;
	}
	offset += written;
    }

    //printf(" data sent... ");
    //fflush(stdout);
    
    char read_buf[HEADSIZE+1];
    bzero(read_buf,HEADSIZE+1);
    int read_cnt = read(sockfd,read_buf,HEADSIZE);  //Could block a while
    if (read_cnt < 0) {
        error("ERROR reading from socket in client");
	return 1; 
         
    }

    //test that the response shows the correct number of bytes were received
    if (bytes != atoi(read_buf) ) {
	error("ERROR: Data transfer incomplete");
	return 1;
    }

    //printf("%s...",read_buf);
    //printf("response received... ");
    //fflush(stdout);  

    close(sockfd);
    //printf("connection closed\n");
    return 0;
}

static PyObject * catanAX25_send_dgram(PyObject *self, PyObject *args)
{
    char *port = "";
    char *dest_call = "";
    char *message = "";
    int message_size;

    PyArg_ParseTuple(args, "sss#", &port, &dest_call, &message, &message_size);

    int result = send_ax25_dgram(port, dest_call, message, message_size);
    return Py_BuildValue("i", result);
}

static PyObject * catanAX25_send_connected(PyObject *self, PyObject *args)
{
    char *port = "";
    char *dest_call = "";
    char *message = "";

    PyArg_ParseTuple(args, "sss", &port, &dest_call, &message);

    int result = send_ax25_packet(port, dest_call, message);
    return Py_BuildValue("i", result);
}

static PyMethodDef catanAX25_methods[] = {
    {"send_dgram", (PyCFunction)catanAX25_send_dgram, METH_VARARGS, "Send an unreliable datagram packet via AX25\n  usage: send_dgram(<port>, <dest callsign>, <message>)"},
    {"send_connected", (PyCFunction)catanAX25_send_connected, METH_VARARGS, "Send data via an AX25 connection"},
    {NULL}
};

void initcatanAX25(void)
{
    Py_InitModule3("catanAX25", catanAX25_methods, "AX25 Extension Module for CATAN");
    init_ports();
}


