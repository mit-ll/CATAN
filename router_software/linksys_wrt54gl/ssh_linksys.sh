#!/bin/sh
# © 2015 Massachusetts Institute of Technology

# Set the Node Name
echo "Changing the hostname to $1"
sed -i /etc/config/system \
    -e "s/'hostname.*$/'hostname' '$1'/"
sed -i /etc/nvram \
    -e "s/node.*$/node=$1'/"

# Set the SSID
echo "Setting the SSID"
sed -i /etc/config.mesh/_setup \
    -e "s/wifi_ssid = .*$/wifi_ssid = CATAN-BACKEND/"

# update the firewall
echo "Updating the firewall rules"
printf "\n" >> /etc/config/firewall
echo "accept:wifi:dport=11113" >> /etc/config/firewall
printf "\n" >> /etc/config/firewall

# Set the bridge binary to start on boot
echo "Adding broadcast bridge to init.d"
cat > /etc/init.d/catan <<EOL
#!/bin/sh /etc/rc.common

START=50
STOP=50

start()
{
    broadcast_bridge wl0 eth0.0 &
    broadcast_bridge eth0.0 wl0 &
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

