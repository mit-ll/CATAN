if [ $# -ne 2 ]; then

	echo "Usage: $0 <ip address of pi> <Node ID of Pi>"
else

	IP=$1
	NODE_ID=$2

	dpkg -s sshpass > /dev/null || (echo "Installing sshpass..." && sudo apt-get -y install sshpass)

	# Upload our deb
	sshpass -p "raspberry" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no distribution/*.deb pi@$IP:~

	# Router software
	sshpass -p "raspberry" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no -r router_software/linksys_wrt54gl pi@$IP:~
	sshpass -p "raspberry" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no -r router_software/ubiquiti_rocket2 pi@$IP:~


	# Run our local setup script
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP 'sudo bash -s' < raspberry-pi/catan_setup.sh

	# Install our deb
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP 'yes | sudo dpkg -i *.deb || ( yes | sudo apt-get install -f)' 

	# Set our node id
	sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP "sudo sed -i -e 's/node_id=.*/node_id=${NODE_ID}/' /opt/catan/conf/catan.conf && sudo service catan restart && sudo sed -i -e 's/raspberrypi/CATAN-${NODE_ID}/' /etc/hosts && sudo sed -i -e 's/raspberrypi/CATAN-${NODE_ID}/' /etc/hostname && sudo /etc/init.d/hostname.sh"

fi
