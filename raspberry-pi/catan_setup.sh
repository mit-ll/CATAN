#!/bin/bash

### make sure that this script is executed from root
if [ $(whoami) != 'root' ]
then
    echo "
This script should be executed as root or with sudo:
    sudo $0
"
    exit 1
fi


printf "Updating APT...\n"
sudo apt-get update > /dev/null || (echo "* Apt-get failed.  (Do you have a proxy setup?)" && exit)

printf "Upgrading packages"
sudo apt-get -y upgrade


printf "Installing dependencies . . .\n"
### Install apache, sqlite, hostapd and dhcp server for front end Wi-Fi
### Purge any old versions to ensure we have clean configs
apt-get -y purge hostapd isc-dhcp-server > /dev/null
apt-get -y install sqlite3 python-flask supervisor hostapd isc-dhcp-server vim sshpass tcpdump python-dateutil python-netifaces python-requests python-pip > /dev/null

sudo pip --proxy http://155.34.234.20:8080 install requests

### Install AX25 stuff - currently not used
# apt-get -y install libax25 libax25-dev ax25-tools ax25-apps 


if grep -q "CATAN" /etc/network/interfaces
then
        echo "* Intefaces already configured."
else

	### Setup network interfaces
	printf "Configuring network interfaces...\n"
	cp -n /etc/network/interfaces{,.bak}
	sed -i /etc/network/interfaces \
#	    -e 's/^auto wlan0/#auto wlan0/' \
#	    -e 's/^iface wlan0/#iface wlan0/' \
#	    -e 's/^wpa-roam/#wpa-roam/' \
	    -e 's/^iface default inet dhcp/#iface default inet dhcp/'
            -e 's/iface eth0 inet manual/iface eth0 inet dhcp/'

	cat <<EOF >> /etc/network/interfaces
# CATAN
iface wlan0 inet static
  address 192.168.2.1
  netmask 255.255.255.0
  post-up /bin/sleep 1; service hostapd start; service isc-dhcp-server start
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

fi


### Configure Wi-Fi hotspot
printf "Configuring front end Wi-Fi...\n"

wifi_interface="wlan0"
ssid="CATAN-AP"

# Configure ifplugd just to do stuff with eth0 and not all interfaces
#http://sirlagz.net/2013/02/10/how-to-use-the-raspberry-pi-as-a-wireless-access-pointrouter-part-3b/
printf "  Configuring /etc/default/ifplugd...\n"
cp -n /etc/default/ifplugd{,.bak}
sed -i 's/^INTERFACES="auto"/INTERFACES="eth0"/' /etc/default/ifplugd
sed -i 's/^HOTPLUG_INTERFACES="all"/HOTPLUG_INTERFACES="eth0"/' /etc/default/ifplugd


### Setup DHCP
### set the INTERFACES on /etc/default/isc-dhcp-server
printf "  Configuring /etc/default/isc-dhcp-server...\n"
cp -n /etc/default/isc-dhcp-server{,.bak}
sed -i "s/^INTERFACES=.*/INTERFACES=\"${wifi_interface}\"/" /etc/default/isc-dhcp-server

### modify /etc/dhcp/dhcpd.conf
printf "  Configuring /etc/dhcp/dhcpd.conf\n"
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
printf "  Configuring /etc/hostapd/hostapd.conf...\n"
cat <<EOF > /etc/hostapd/hostapd.conf
interface=$wifi_interface
driver=nl80211
ssid=$ssid
hw_mode=g
channel=6
EOF

### modify /etc/default/hostapd
printf "  Configuring /etc/default/hostapd...\n"
cp -n /etc/default/hostapd{,.bak}
sed -i /etc/default/hostapd \
    -e 's:^DAEMON_CONF=.*:DAEMON_CONF="/etc/hostapd/hostapd.conf":'
sed -i /etc/default/hostapd \
    -e 's:^#DAEMON_CONF=.*:DAEMON_CONF="/etc/hostapd/hostapd.conf":'

### Restart DHCP server
printf "  Restarting DHCP server..."
ifconfig wlan0 192.168.2.1
service isc-dhcp-server restart

### Restart hostapd (Must be first to set the ip)
printf "  Restarting Wi-Fi access point..."
service hostapd restart
ifconfig wlan0 192.168.2.1

### Set to start on boot
sudo update-rc.d hostapd enable 
sudo update-rc.d isc-dhcp-server enable


## Network sharing
printf "  Configuring network sharing.../"
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
echo "options ath9k nohwcrypt=1" | sudo tee /etc/modprobe.d/ath9k.conf
#sudo sh -c "echo blacklist acer-wmi >> /etc/modprobe.d/blacklist.conf"
