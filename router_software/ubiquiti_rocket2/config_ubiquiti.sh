#!/bin/bash
# © 2015 Massachusetts Institute of Technology
# Configures a Ubiquiti Rocket M2 flashed with stock Broadband Hamnet image
# to work with CATAN

PASSWORD="hsmm"

# Install sshpass if not installed
dpkg -s sshpass > /dev/null || (echo "Installing sshpass..." && sudo apt-get -y install sshpass)

printf "\nReady to configure Ubiquiti Rocket M2 router to work with CATAN.  Please ensure that the router is flashed with stock Broadband Hamnet firmware and that you have received an IP address from it over DHCP.\n\n"

# Grab the node name
# Remind user of legal requirements for using call sign
printf "Please enter your callsign:\n"
read CALLSIGN

printf "Please enter the node id:\n"
read NODE_ID

NODE_NAME=CATAN-${NODE_ID}-${CALLSIGN}

# Upload the binary
printf "Uploading broadcast bridge binary via scp. Using password '$PASSWORD'\n"
sshpass -p $PASSWORD scp -o PubKeyAuthentication=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -P 2222 broadcast_bridge_a71xxx root@localnode:/bin/broadcast_bridge

# Upload the config script
printf "Uploading configuration script. Using password '$PASSWORD'\n"
sshpass -p $PASSWORD scp -o PubKeyAuthentication=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -P 2222 ssh_ubiquiti.sh root@localnode:/tmp

# ssh into localnode and run the config script
printf "Attempting to ssh into the router at 'localnode'. Using password '$PASSWORD'\n"
sshpass -p $PASSWORD ssh -o PubKeyAuthentication=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -p 2222 root@localnode 'chmod +x /tmp/ssh_ubiquiti.sh; /tmp/ssh_ubiquiti.sh '${NODE_NAME}''

printf "Done!  Please remember to change the router's default password!\n"
