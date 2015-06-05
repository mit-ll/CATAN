#!/bin/ash
# © 2015 Massachusetts Institute of Technology

# Set the Node Name
echo "Changing the hostname to $1"
sed -i /etc/config/system \
    -e "s/'hostname.*$/'hostname' '$1'/"
sed -i /etc/local/uci/hsmmmesh \
    -e "s/node.*$/node '$1'/"

# Set the SSID
echo "Setting the SSID"
sed -i /etc/config.mesh/_setup \
    -e "s/wifi_ssid = .*$/wifi_ssid = CATAN-BACKEND/"

# update the firewall
echo "Updating the firewall rules"
cat > /etc/config.mesh/firewall.user <<EOL
# This file is interpreted as shell script.
# Put your custom iptables rules here, they will
# be executed with each firewall (re-)start.

iptables -I zone_wifi 1 -p udp --dport 11113 -j ACCEPT
iptables -I zone_dtdlink 1 -p udp --dport 11113 -j ACCEPT
EOL
chmod +x /etc/config.mesh/firewall.user
cp /etc/config.mesh/firewall.user /etc/firewall.user

# Set the bridge binary to start on boot
echo "Adding broadcast bridge to init.d"
cat > /etc/init.d/catan <<EOL
#!/bin/sh /etc/rc.common

START=50
STOP=50

start()
{
    broadcast_bridge wlan0 eth0 &
    broadcast_bridge eth0 wlan0 &
}

stop()
{
    killall broadcast_bridge
}
EOL

chmod +x /etc/init.d/catan
/etc/init.d/catan enable

# Reboot
echo "Rebooting"
reboot

