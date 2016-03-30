#!/usr/bin/env bash

echo ""
echo "+---------------------------------------------------------------------------------------+"
echo ""
echo "You must first resize the disk on your Raspberry Pi and enable ssh using: 'sudo raspi-config' on the Pi."
echo ""
echo "+----------------------------------------------------------------------------------------+"
echo ""

if [ $# -ne 2 ]; then

	echo "Usage: $0 <ip address of pi> <Node ID of Pi>"
else

	IP=$1
	NODE_ID=$2

	dpkg -s sshpass > /dev/null || (echo "Installing sshpass..." && sudo apt-get -y install sshpass)

	# Router software
	echo "* Copying router software to the Pi..."
	sshpass -p "raspberry" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no -r router_software/linksys_wrt54gl pi@$IP:~ > /dev/null 2>&1
	sshpass -p "raspberry" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no -r router_software/ubiquiti_rocket2 pi@$IP:~ > /dev/null 2>&1

	# Run our local setup script
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP 'sudo bash -s' < raspberry-pi/catan_setup.sh

   echo "* Installing CATAN services on the Pi..."
	# Upload our deb
	sshpass -p "raspberry" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no distribution/*.deb pi@$IP:~
	# Install our deb
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP 'yes | sudo dpkg -i *.deb || ( yes | sudo apt-get install -f)'

   echo "Setting the CATAN node ID on the Pi..."
	# Set our node id
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP "sudo sed -i -e 's/node_id=.*/node_id=${NODE_ID}/' /opt/catan/conf/catan.conf && sudo service catan restart && sudo sed -i -e 's/raspberrypi/CATAN-${NODE_ID}/' /etc/hosts && sudo sed -i -e 's/raspberrypi/CATAN-${NODE_ID}/' /etc/hostname && sudo /etc/init.d/hostname.sh" > /dev/null 2>&1

   echo "All done! Rebooting the Pi..."
	# Set our node id
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP "sudo shutdown -r now" > /dev/null 2>&1

fi
