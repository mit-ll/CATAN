#!/usr/bin/env bash
#/sbin/ifconfig mon.wlan0 >/dev/null || (sudo service hostapd restart && sudo service isc-dhcp-server restart)
# Check if gedit is running
if pgrep "dhcpd" > /dev/null
then
    sudo service isc-dhcp-server restart
else
    sudo service isc-dhcp-server restart
fi