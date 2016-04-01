#!/bin/bash

export TERM=vt102
BOLD="\033[1m"
RED="\033[0;31m"

### make sure that this script is executed from root
if [ $(whoami) != 'root' ]
then
    echo "
This script should be executed as root or with sudo:
    sudo $0
"
    exit 1
fi


echo -e "${RED}${BOLD}* Updating APT..."
tput sgr0
sudo apt-get update > /dev/null 2>&1 || (echo "* Apt-get failed.  (Do you have a proxy setup?)" && exit)

echo -e "${RED}${BOLD}* Upgrading all packages (This can take a while...)"
tput sgr0
sudo apt-get -y upgrade


echo -e "${RED}${BOLD}* Installing dependencies..."
tput sgr0
### Install apache, sqlite, hostapd and dhcp server for front end Wi-Fi
### Purge any old versions to ensure we have clean configs
apt-get -y --force-yes purge hostapd isc-dhcp-server
apt-get -y --force-yes install sqlite3 python-flask supervisor hostapd isc-dhcp-server vim sshpass tcpdump python-dateutil python-netifaces python-requests python-pip python-serial

sudo pip install requests

### Install AX25 stuff - currently not used
# apt-get -y install libax25 libax25-dev ax25-tools ax25-apps 


if grep -q "CATAN" /etc/network/interfaces
then
   echo -e "${RED}${BOLD}* Network interfaces already configured."
   tput sgr0
else

	### Setup network interfaces
	echo -e "${RED}${BOLD}* Configuring network interfaces..."
	tput sgr0
	cp -n /etc/network/interfaces{,.bak}
	sed -i /etc/network/interfaces \
	    -e 's/^iface default inet dhcp/#iface default inet dhcp/'
       -e 's/iface eth0 inet manual/iface eth0 inet dhcp/'

	cat <<EOF >> /etc/network/interfaces

# CATAN
iface wlan0 inet static
  address 192.168.2.1
  netmask 255.255.255.0
  post-up /bin/sleep 3; service hostapd start; service isc-dhcp-server start
  pre-down service hostapd stop; service isc-dhcp-server stop

allow-hotplug eth1
auto eth1
iface eth1 inet dhcp

allow-hotplug eth2
auto eth2
iface eth2 inet static
  address 192.168.0.3
  netmask 255.255.255.0

EOF

	cat <<EOF >> /etc/dhcpcd.conf

# CATAN
interface wlan0
static ip_address=192.168.2.1/24
interface eth2
static ip_address=192.168.0.3/24


EOF

fi


### Configure Wi-Fi hotspot
echo -e "${RED}${BOLD}* Configuring front end Wi-Fi..."
tput sgr0

wifi_interface="wlan0"
ssid="CATAN-AP"

# Configure ifplugd just to do stuff with eth0 and not all interfaces
#http://sirlagz.net/2013/02/10/how-to-use-the-raspberry-pi-as-a-wireless-access-pointrouter-part-3b/
#echo -e "${RED}*  Configuring /etc/default/ifplugd..."
#tput sgr0
#cp -n /etc/default/ifplugd{,.bak}
#sed -i 's/^INTERFACES="auto"/INTERFACES="eth0"/' /etc/default/ifplugd
#sed -i 's/^HOTPLUG_INTERFACES="all"/HOTPLUG_INTERFACES="eth0"/'
# /etc/default/ifplugd


### Setup DHCP
### set the INTERFACES on /etc/default/isc-dhcp-server
echo -e "${RED}*  Configuring /etc/default/isc-dhcp-server..."
tput sgr0
cp -n /etc/default/isc-dhcp-server{,.bak}
sed -i "s/^INTERFACES=.*/INTERFACES=\"${wifi_interface}\"/" /etc/default/isc-dhcp-server

### modify /etc/dhcp/dhcpd.conf
echo -e "${RED}*  Configuring /etc/dhcp/dhcpd.conf"
tput sgr0
cp -n /etc/dhcp/dhcpd.conf{,.bak}
sed -i /etc/dhcp/dhcpd.conf \
    -e 's/^option domain-name/#option domain-name/' \
    -e 's/^option domain-name-servers/#option domain-name-servers/' \
    -e 's/^default-lease-time/#default-lease-time/' \
    -e 's/^max-lease-time/#max-lease-time/'

# authoritative
sed -i /etc/dhcp/dhcpd.conf \
    -e 's/^#authoritative/authoritative/'

cat <<EOF >> /etc/dhcp/dhcpd.conf

# CATAN dhcp server config
subnet 192.168.2.0 netmask 255.255.255.0 {
        range 192.168.2.2 192.168.2.102;
        default-lease-time 600;
        max-lease-time 7200;
        option domain-name-servers 192.168.2.1, 192.168.2.1;
        option routers 192.168.2.1;
}
EOF


### Configure hostapd

### create /etc/hostapd/hostapd.conf
echo -e "${RED}*  Configuring /etc/hostapd/hostapd.conf..."
tput sgr0
cat <<EOF > /etc/hostapd/hostapd.conf
interface=$wifi_interface
driver=nl80211
ssid=$ssid
hw_mode=g
channel=6
EOF

### modify /etc/default/hostapd
echo -e "${RED}*  Configuring /etc/default/hostapd..."
tput sgr0
cp -n /etc/default/hostapd{,.bak}
sed -i /etc/default/hostapd \
    -e 's:^DAEMON_CONF=.*:DAEMON_CONF="/etc/hostapd/hostapd.conf":'
sed -i /etc/default/hostapd \
    -e 's:^#DAEMON_CONF=.*:DAEMON_CONF="/etc/hostapd/hostapd.conf":'

# Kill the networking daemon
echo -e "${RED}* Disabling networking services..."
tput sgr0
sudo systemctl stop networking.service > /dev/null 2>&1
sudo systemctl disable networking.service > /dev/null 2>&1

### Restart DHCP server
echo -e "${RED}*  Restarting DHCP server..."
tput sgr0
ifconfig wlan0 192.168.2.1
service isc-dhcp-server restart

### Restart hostapd (Must be first to set the ip)
echo -e "${RED}*  Restarting Wi-Fi access point..."
tput sgr0
service hostapd restart
ifconfig wlan0 192.168.2.1

### Set to start on boot
sudo update-rc.d hostapd enable 
sudo update-rc.d isc-dhcp-server enable


## Network sharing
echo -e "${RED}*  Configuring network sharing..."
tput sgr0
sudo sed -i -e 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /etc/sysctl.conf
sudo sh -c "echo 1 > /proc/sys/net/ipv4/ip_forward"

sudo iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE
sudo iptables -A FORWARD -i eth1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlan0 -o eth1 -j ACCEPT

sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"

sudo sh -c "echo 'up iptables-restore < /etc/iptables.ipv4.nat' >> /etc/network/interfaces"


# BUGFIX: Somehow eth0 is getting changed!
sed -i /etc/network/interfaces -e 's/iface eth0 inet manual/iface eth0 inet dhcp/'



# Setup a contrab job to continously check that our access point is up.
(sudo crontab -l; echo "* * * * * /opt/catan/scripts/check_wifi.sh > /opt/catan/log/crontab.log 2>&1") | sudo crontab - 

# Fix WiFi Driver
echo -e "${RED}${BOLD}* Attempting WiFi patch."
tput sgr0
echo "options ath9k nohwcrypt=1" | sudo tee /etc/modprobe.d/ath9k.conf
#sudo sh -c "echo blacklist acer-wmi >> /etc/modprobe.d/blacklist.conf"
