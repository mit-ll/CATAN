// © 2015 Massachusetts Institute of Technology

#include <stddef.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/un.h>

//#define SERVER  "/tmp/serversocket_dgram"
#define MAXMSG  512

int
make_named_socket (const char *filename)
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

  if (bind (sock, (struct sockaddr *) &name, size) < 0)
    {
      perror ("bind");
      exit (EXIT_FAILURE);
    }

  return sock;
}

int
main (int argc, char *argv[])
{
  int sock;
  char message[MAXMSG];
  struct sockaddr_un name;
  //size_t size;
  socklen_t size;
  int nbytes;
  char *serverfile;

  if (argc < 2) {
	fprintf(stderr, "usage %s <server_socket_file> \n", argv[0]);
        exit(1);
  } else {
  	serverfile = argv[1];
  }
  /* Remove the filename first, it’s ok if the call fails */
  unlink (serverfile);

  /* Make the socket, then loop endlessly. */
  sock = make_named_socket (serverfile);
  while (1)
    {
      /* Wait for a datagram. */
      size = sizeof (name);
      nbytes = recvfrom (sock, message, MAXMSG, 0,
                         (struct sockaddr *) & name, &size);
      if (nbytes < 0)
      {
          perror ("recfrom (server)");
          exit (EXIT_FAILURE);
      }
      message[nbytes] = 0; //add null byte to end of string;

      // Give a diagnostic message
      fprintf (stderr, "Server: got message: %s\n", message);

      /*
      // Bounce the message back to the sender
      nbytes = sendto (sock, message, nbytes, 0,
                       (struct sockaddr *) & name, size);
      if (nbytes < 0)
        {
          perror ("sendto (server)");
          exit (EXIT_FAILURE);
        }
       */
    }
}
