// © 2015 Massachusetts Institute of Technology

#include <stddef.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/un.h>

#define SERVER  "/tmp/serversocket"
#define CLIENT  "/tmp/mysocket"
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

  unlink(filename);  //try to unlink before binding

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
  //char message[MAXMSG];
  struct sockaddr_un name;
  ssize_t size;
  int nbytes;

  char *message = argv[1];
  nbytes = strlen(message);  

  sock = make_named_socket (CLIENT);

  name.sun_family = AF_LOCAL;
  strcpy(name.sun_path, SERVER);
  size = sizeof (name);
  //size = strlen (name.sun_path) + sizeof (name.sun_family);

  nbytes = sendto (sock, message, nbytes+1, 0,
                  (struct sockaddr *) &name, size);

  if (nbytes < 0)
  {
    perror ("client send error");
    exit (EXIT_FAILURE);
  }

  /* Give a diagnostic message. */
  fprintf (stderr, "Client: sent message: %s\n", message);

  /* Clean up */
  remove(CLIENT);
  close(sock);
}
