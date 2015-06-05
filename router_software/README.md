# Setting up routers for Wi-Fi mesh for CATAN

1. Make sure your router is supported by the [HAMNET project](http://broadband-hamnet.org/).

2. Download and flash the correct firmware for your router.

3. Wait for router to reboot.  Folllow the setup instructions [here](http://www.broadband-hamnet.org/documentation/68-firmware-installation-instructions.html).  Default login is user:root, pw:hsmm
   Under setup, you should change the node name and the SSID.  Make sure that the SSID is the same for all of your nodes.  Default login is user:root, pw:hsmm

4. You should now have a working mesh node.  However, by default there's no way to do UDP broadcast using builtin utilities and such.  So, we need to take the following steps.

5. Compile the broadcast_bridge binary (if needed) and copy it over to router.  This will bridge UDP broadcast packets received on the wired interface to the mesh interface and vice versa.

6. Using iptables, punch a hole in the firewall rules to allow packets on the mesh interface on the specific port that you are using.  By default the firmware blocks all but a few ports (e.g. 2222 for ssh).  The rules should be in /etc/config/firewall

Don't forget to restart the firewall! /etc/init.d/firewall restart


# Building cross-compiled binary

	./setup_build_environment.sh  (Select processor for your router)

	./build_cross_compiled.sh  (This is an example for MIPS)

# Problems

- During configuration we sometimes had trouble with 'localnode' not resolving.  To fix this jsut edit your /etc/resolv.conf and put the mesh node ip first in the list.

# © 2015 Massachusetts Institute of Technology