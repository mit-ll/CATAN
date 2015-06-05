// © 2015 Massachusetts Institute of Technology

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <netax25/ax25.h>
#include <netax25/axlib.h>
#include <netax25/axconfig.h>
#include <linux/if.h>
#include <linux/if_ether.h>

#define BUFSIZE 255

#define AXALEN 7
#define E_BIT 0x01	/* Address extension bit */
#define REPEATED 0x80	/* Has-been-repeated bit */
#define MAX_PORTS 16
#define AX25_UI 0x03

#define ASCII_ADDR_LEN 9

#define SERVER  "/tmp/serversocket_dgram"
#define CLIENT  "/tmp/clientsocket_dgram"
#define MAXMSG  512

typedef struct {
    char dest[ASCII_ADDR_LEN];
    char src[ASCII_ADDR_LEN];
    unsigned char ctl;
    unsigned char pid;
    char info[BUFSIZE];
    int info_size;
} ax25_packet;

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

void print_call(unsigned char *bptr) {
	printf("%c%c%c%c%c%c-%d", bptr[0] >> 1, bptr[1] >> 1,
			bptr[2] >> 1, bptr[3] >> 1, bptr[4] >> 1, 
			bptr[5] >> 1, (bptr[6] >> 1) & 0xf);
}

int call_to_ascii(unsigned char *bptr, 
		  char *buffer, 
		  int buff_size) {

	int n = snprintf(buffer, buff_size, "%c%c%c%c%c%c-%d", 
			  bptr[0] >> 1, bptr[1] >> 1,
			  bptr[2] >> 1, bptr[3] >> 1, bptr[4] >> 1, 
			  bptr[5] >> 1, (bptr[6] >> 1) & 0xf);

	//check that the write was successful
	if (n >= 0 && n < buff_size) {
	    return 0;
	} else {
	    return -1;
	}
}

//parse_packet:  returns the number of bytes in message if success
//               or -1 on failure
int parse_packet(unsigned char *buf, 
		int size, 
		ax25_packet *new_packet) {
    
    	unsigned char *bptr;
	int count, n;
	unsigned char *call;

	int for_me = 0;
        int UI_packet = 0;
        int remaining = size;
	
	//Decode the AX.25 Packet 

	/* Find packet, skip over flag */
	bptr = buf+1;
        remaining -= 1;

	/* Now at destination address */
        char dest[ASCII_ADDR_LEN];
        if (call_to_ascii(bptr, new_packet->dest, ASCII_ADDR_LEN)) {
	    return -1;
	} 
	bptr += AXALEN;
        remaining -= AXALEN;
	
	/* Now at source address */
        if (call_to_ascii(bptr, new_packet->src, ASCII_ADDR_LEN)) {            
	    return -1;
	} 
	if (!(bptr[6] & E_BIT))
	{
	    //printf("There is a digipeater address?\n");
	}

	/* Now at digipeaters */
        //The E_BIT (in the last byte) is set for the last address field
        count = 0;
	while( !(bptr[6] & E_BIT) ) {
            printf("count = %d\n", count);
	    if ( (count > AX25_MAX_DIGIS) || ( (bptr - buf)+6 > size) ) {
                return -1;
            }
	    bptr += AXALEN;
            remaining -= AXALEN;
            count++;
	}
	bptr += AXALEN;
        remaining -= AXALEN;

	// Now at control field (0x03 means UI frame)
	new_packet->ctl = bptr[0];
        bptr++;
        remaining--;

	// Now at Protocol ID field (0xf0 (240) means no layer 3 protocol)
	new_packet->pid = bptr[0];
        bptr++;
        remaining--;

        //Now at information field
        memcpy(new_packet->info, bptr, remaining);
        new_packet->info_size = remaining;
        return remaining;

	/*
        //Fixed- don't use string function here!!
        //Now at information field
	n = snprintf(new_packet->info, BUFSIZE, "%s", bptr);
	//check that the write was successful
	if (n >= 0 && n < BUFSIZE) {
	    //success
	    return n;
	} else {
	    //error
	    return -1;
	}
        return -1;  //not reached
        */
}

int print_packet(struct _IO_FILE *output, 
		ax25_packet *new_packet, 
		char *mycall) {
        if (new_packet->ctl == AX25_UI) {
	    //if UI packet
            if (!strncmp(new_packet->dest, mycall, ASCII_ADDR_LEN)) {
	    	//for my callsign
		fprintf(output, "%s->**ME**=%s\n", new_packet->src, 
							  new_packet->info);
   	    } else {
            	//for another callsign
		fprintf(output, "%s->%s=%s\n", new_packet->src, 
							new_packet->dest,
						 	new_packet->info);
	    }
 	} else {
	    //if non-UI packet
	    fprintf(output, "NON-UI from %s: CTL=%d\n", new_packet->src, 
					      (unsigned int) new_packet->ctl);
	}
 	return 0;
}

int build_message_to_layer3(ax25_packet *packet, 
			   unsigned char *buf, 
			   int size) {
    int n = snprintf(buf, size, "%s:%s:", 
		     packet->src, packet->dest);
    //n holds the number of bytes written excluding the null byte
    //check that the write was successful
    if (!(n >= 0 && n < size)) {
	return -1;
    }
    //check that the memcpy won't exceed the size of the buffer
    if (n + packet->info_size > size) {
	return -1;
    }
    memcpy(buf+n, packet->info, packet->info_size);

    //return the number of bytes written to the buffer
    return n + packet->info_size;
}

int make_named_socket (const char *filename)
{
  struct sockaddr_un name;
  int sock;
  size_t size;

  /* Create the socket. */
  sock = socket (PF_LOCAL, SOCK_DGRAM, 0);
  if (sock < 0)
    {
      perror ("socket");
      exit (EXIT_FAILURE);
    }

  /* Bind a name to the socket. */
  name.sun_family = AF_LOCAL;
  strncpy (name.sun_path, filename, sizeof (name.sun_path));
  name.sun_path[sizeof (name.sun_path) - 1] = '\0';

  /* The size of the address is
     the offset of the start of the filename,
     plus its length (not including the terminating null byte).
     Alternatively you can just do:
     size = SUN_LEN (&name);
 */
  size = (offsetof (struct sockaddr_un, sun_path)
          + strlen (name.sun_path));

  unlink(filename);  //try to unlink before binding
  if (bind (sock, (struct sockaddr *) &name, size) < 0)
    {
      perror ("bind");
      exit (EXIT_FAILURE);
    }

  return sock;
}


int main(int argc, char *argv[])
{
     int sockfd, newsockfd, portno;
     socklen_t clilen;
     char *callsign;
     int s, n;
     int addrlen = sizeof(struct full_sockaddr_ax25);

     char buffer[BUFSIZE];
     char message_buf[MAXMSG];
     struct full_sockaddr_ax25 serv_addr, cli_addr;
     ax25_packet packet;

     if (argc < 2) {
         //fprintf(stderr,"ERROR, no callsign provided\n");
         fprintf(stderr,"usage %s <server_callsign> \n", argv[0]);
         exit(1);
     }else {
         callsign = argv[1];
         fprintf(stdout, "Listening on %s\n", callsign);
     }

     //sockfd = socket(AF_AX25, SOCK_SEQPACKET, 0);
     //sockfd = socket(AF_AX25, SOCK_DGRAM, 0);
     //sockfd = socket(AF_INET, SOCK_PACKET, htons(ETH_P_AX25));  //raw (old)
     sockfd = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_AX25));  //raw (new)

     if (sockfd < 0) 
        error("ERROR opening socket");

     if (ax25_config_load_ports() == 0) {
	 error("Problem loading axports file");
	 exit(1);
     }


     bzero((char *) &serv_addr, sizeof(serv_addr));
     ax25_aton(callsign, &serv_addr); 

     //Set up local socket to forward packets
     int localsock;
     struct sockaddr_un servername;
     ssize_t servername_size;

     localsock = make_named_socket (CLIENT);
     servername.sun_family = AF_LOCAL;
     strcpy(servername.sun_path, SERVER);
     servername_size = sizeof (servername);

     int recv_bytes, send_bytes, message_size;
     while (1)
     {
      	/* Wait for a datagram. */
	bzero((char *) &buffer, BUFSIZE);
	bzero((char *) &cli_addr, sizeof(cli_addr));
      	recv_bytes = recvfrom (sockfd, buffer, BUFSIZE, 0,
                         (struct sockaddr *) &cli_addr, &clilen);
        //printf("recv_bytes = %u\n", (unsigned int) recv_bytes);
     	if (recv_bytes < 0) {
            perror ("recvfrom (server)");
            continue;
	} else if (recv_bytes == 0) {
	    fprintf(stdout, "Server: got zero bytes\n");
            continue;
	}
	bzero((char *) &packet, sizeof(packet));
        
	if (parse_packet(buffer, recv_bytes, &packet) < 0) {
	    printf("parse_packet failure\n");
            continue;
	}

        //if a UI packet forward to higher layer
        if (packet.ctl == AX25_UI) {
	    //build message to pass to higher layer protocol
	    bzero((char *) &message_buf, MAXMSG);
            printf("Received message with %d byte payload\n",  packet.info_size);
	    message_size = build_message_to_layer3(&packet, message_buf, MAXMSG);
	    if (message_size < 0) {
	        perror("error building layer3 message");
	    }
	    //printf("Message=%s\n", message_buf);
	    //print_packet(stdout, &packet, callsign);

	    //forward data to local socket
  	    send_bytes = sendto (localsock, message_buf, message_size, 0,
	                        (struct sockaddr *) &servername, servername_size);
  	    if (send_bytes < 0) {
  	        perror ("localsocket send error");
	        //exit (EXIT_FAILURE);
	    }
        }
     }

     /* Clean up */
     remove(CLIENT);
     close(localsock);

     close(newsockfd);
     close(sockfd);
     return 0; 
}



