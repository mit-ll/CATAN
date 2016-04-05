IP=$1
NODE_ID=$2

sshpass -p "raspberry" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o PubKeyAuthentication=no pi@$IP "sudo sed -i -e 's/node_id=.*/node_id=${NODE_ID}/' /opt/catan/conf/catan.conf && sudo service catan restart && sudo sed -i -e 's/raspberrypi/CATAN-${NODE_ID}/' /etc/hosts && sudo sed -i -e 's/raspberrypi/CATAN-${NODE_ID}/' /etc/hostname && sudo /etc/init.d/hostname.sh" > /dev/null 2>&1
