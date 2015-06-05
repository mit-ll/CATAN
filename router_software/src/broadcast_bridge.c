#include<stdio.h> //for printf
#include<string.h> //memset
#include<sys/socket.h>    //for socket ofcourse
#include<arpa/inet.h> // inet_addr
#include<stdlib.h> //for exit(0);
#include<errno.h> //For errno - the error number
#include<netinet/udp.h>   //Provides declarations for udp header
#include<netinet/ip.h>    //Provides declarations for ip header
#include <net/if.h>  // Bind to interface
#include <sys/ioctl.h>
#include <netpacket/packet.h>

#define MAX_UDP 65535
#define FORWARD_PORT 11113
#define FORWARD_MASK 0

#define VERBOSE 0

int main (int argnum, char **argv)
{
	if (argnum < 3) {
		printf("Usage: %s <input interface> <output interface>\n", argv[0]);
		exit(-1);
	}

	printf("Reading broadcast packets from %s and relaying to %s..\n",
			argv[1],argv[2]);

    //Create a raw socket of type IPPROTO
	int s_in = socket (AF_INET, SOCK_RAW, IPPROTO_UDP);
	int s_out = socket (AF_INET, SOCK_RAW, IPPROTO_UDP);

    if(s_out == -1)
    {
        //socket creation failed, may be because of non-root privileges
        perror("Failed to create raw socket");
        exit(1);
    }

    // Bind to our actual interface
	struct ifreq ifr_in;
	struct ifreq ifr_out;
	memset(&ifr_in, 0, sizeof(ifr_in));
	memset(&ifr_out, 0, sizeof(ifr_out));

	//
	// Input binding
	//
	strncpy(ifr_in.ifr_name, argv[1], sizeof(ifr_in.ifr_name));

	// Bind to interface
	if (setsockopt(s_in, SOL_SOCKET, SO_BINDTODEVICE, (void *)&ifr_in, sizeof(ifr_in)) < 0) {
		perror("Could not bind to interface.");
		// If something wrong just exit
		exit(-1);
	}

	// Get our ip
	if (ioctl(s_out, SIOCGIFADDR, &ifr_in) < 0)
		perror("SIOCGIFADDR");

	// display result
	struct in_addr ip_in = ((struct sockaddr_in *)&ifr_in.ifr_addr)->sin_addr;

	//
	// Output binding
	//
	strncpy(ifr_out.ifr_name, argv[2], sizeof(ifr_out.ifr_name));
	if (setsockopt(s_out, SOL_SOCKET, SO_BINDTODEVICE, (void *)&ifr_out, sizeof(ifr_out)) < 0) {
		perror("Could not bind to interface.");
		// If something wrong just exit
		exit(-1);
	}

	// allow broadcast messages for the socket
	int true = 1;
	if (setsockopt(s_out, SOL_SOCKET, SO_BROADCAST, &true, sizeof(true))) {
		printf ("Could not set SO_BROADCAST (%s)\n", strerror(errno));
		exit (-1);
	}

	// Don't include headers by default.
//	int hdrincl=1;
//	if (setsockopt(s_out,IPPROTO_IP,IP_HDRINCL,&hdrincl,sizeof(hdrincl))==-1) {
//	    printf("%s",strerror(errno));
//	    exit(-1);
//	}

	// Get our ip
	if (ioctl(s_out, SIOCGIFADDR, &ifr_out) < 0)
		perror("SIOCGIFADDR");

	// display result
	struct in_addr ip_out = ((struct sockaddr_in *)&ifr_out.ifr_addr)->sin_addr;

	printf("Bound input to: %s\n", inet_ntoa(ip_in));
	printf("Bound output to: %s\n", inet_ntoa(ip_out));

    //Datagram to represent the packet
    char datagram[MAX_UDP];
//    char *data;

    //zero out the packet buffer
    memset (datagram, 0, 4096);

    //IP header
    struct iphdr *iph = (struct iphdr *) datagram;

    //UDP header
    struct udphdr *udph = (struct udphdr *) (datagram + sizeof(struct iphdr));

    //Data part
//    data = datagram + sizeof(struct iphdr) + sizeof(struct udphdr);


    // What ip do we forward to?
    struct sockaddr_in sin;
    sin.sin_family = AF_INET;
    sin.sin_port = htons(FORWARD_PORT);
    sin.sin_addr.s_addr = inet_addr ("255.255.255.255");

    // Receive data
    struct sockaddr_in recv_sa;
    int read_bytes = 0;
    int recvlen = sizeof(recv_sa);

    // Loop forever
    while (1)
    {
    	//Recieve a packet
    	read_bytes = recvfrom(s_in, datagram, sizeof(datagram), 0,
                (struct sockaddr *)&recv_sa, (socklen_t*)&recvlen);
    	if (read_bytes < 0){
			perror("recvfrom failed");
			break;
		}

    	if (VERBOSE && iph->saddr != ip_out.s_addr && iph->saddr != ip_in.s_addr) {
    		printf("Read %d bytes.", read_bytes);
    		printf("Dest IP: %08X, Port: %04X\n",iph->daddr, udph->dest);
    	}

    	//printf("%08X == %08X or %08X?\n", iph->saddr, ip_out.s_addr, ip_in.s_addr);
    	if (iph->saddr == ip_out.s_addr ||
    		iph->saddr == ip_in.s_addr) {
    		if (VERBOSE) {
    			printf("Received a loopback packet, ignoring.\n");
    		}
    		continue;
    	}

    	// Check to see if this is a packet that should be forwarded
    	if ((iph->daddr & FORWARD_MASK) == FORWARD_MASK
    			&& ntohs(udph->dest) == FORWARD_PORT) {

    		if (VERBOSE)
    			printf("Forwarding broadcast packet.\n");

			//Send the packet
		int data_len = ntohs(udph->len);
			if (sendto (s_out,
					udph,
					data_len,
					0, (struct sockaddr *) &sin,
					sizeof (sin)) < 0)
			{
				perror("sendto failed");
				break;
			}
			//Data send successfully
			else if (VERBOSE) {
				printf ("Packet Send. Length : %d \n" , iph->tot_len);
			}
    	}
    }

    return 0;
}
