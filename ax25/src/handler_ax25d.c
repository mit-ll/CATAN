// © 2015 Massachusetts Institute of Technology

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <stdbool.h>
#include <sys/socket.h>
#include <sys/un.h>

#define BUFSIZE 4096
#define HEADSIZE 5  //must match HEADFORMAT
#define HEADFORMAT "%05u"

#define SERVER  "/tmp/serversocket_connected"
#define CLIENT  "/tmp/clientsocket_connected"

void error(const char *msg)
{
    perror(msg);
    exit(1);
}

void remove_newline_ch(char *line)
{
    int new_line = strlen(line)-1;
    if (line[new_line] == '\n') {
        line[new_line] = '\0';
    }
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

int main(int argc, char* argv[])
{
    if (argc < 3) {
	perror("Not enough command line arguments");
    }
    char *packet_src = argv[1];
    char *log_file_name = argv[2];
    
    FILE *logfile = fopen(log_file_name, "a");
    if (!logfile) {
        printf("LOGFILE: %s\n", log_file_name);
	error("Server error opening log file"); 
    }

    //read the header to determine the number of bytes being sent
    char header[HEADSIZE];
    bzero(header, HEADSIZE);
    int read_cnt = fread(header, sizeof(char), HEADSIZE, stdin);
    if (read_cnt < HEADSIZE) {
	fprintf(logfile, "ERROR: Bad header\n");
	exit(1);
    }
    int bytes_to_read = atoi(header);
    if (bytes_to_read > BUFSIZE-1) {
	fprintf(logfile, "ERROR: Packet exceeds max supported size\n");
	exit(1);
    }

    char buffer[BUFSIZE]; 
    bzero(buffer,BUFSIZE);
    int bytes = 0;
    char c;
    //read until the correct number of bytes are received
    do {
    	c = getc(stdin);
        buffer[bytes] = c;
	bytes++;
    } while ( (bytes < bytes_to_read) && (c != EOF) );

    if (bytes < bytes_to_read) {
	fprintf(logfile, "Missing %d bytes\n", bytes_to_read-bytes);
    }
    if (ferror(stdin) ) {
	fprintf(logfile, "Read Error (%d):%s\n", errno, strerror(errno));
    }

    //get the current time
    time_t tm;   
    time(&tm);
    char *time_str = ctime(&tm); 
    remove_newline_ch(time_str); 

    //write incoming packet to LOGFILE
    fprintf(logfile, "%s\t%s\t%s\n", time_str, packet_src, buffer);
    fflush(logfile);

    //Set up local socket to forward packets
    int localsock;
    struct sockaddr_un localname;
    ssize_t localname_size;

    localsock = make_named_socket (CLIENT);
    localname.sun_family = AF_LOCAL;
    strcpy(localname.sun_path, SERVER);
    localname_size = sizeof (localname);

    //forward data to local socket
    int recv_bytes, send_bytes;
    send_bytes = sendto (localsock, buffer, strlen(buffer)+1, 0,
                         (struct sockaddr *) &localname, localname_size);
    if (send_bytes < 0) {
  	perror ("localsocket send error");
	//exit (EXIT_FAILURE);
    }

    //generate response containing HEADSIZE ASCII chars 
    //encoding the length of data received in bytes as a decimal number
    char response[HEADSIZE+1];  
    sprintf(response, HEADFORMAT, (unsigned int) bytes);  
    //sprintf(response, "%05u", (unsigned int) bytes);  
    int response_written = fwrite(response, sizeof(char), strlen(response), stdout);
    fflush(stdout);

    getc(stdin);  	//this should block until the connection is terminated 
			//by the client after it has read the response



    fclose(logfile); 
    return 0; 
}

