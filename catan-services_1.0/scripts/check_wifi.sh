#!/usr/bin/env bash
#/sbin/ifconfig mon.wlan0 >/dev/null || (sudo service hostapd restart && sudo service isc-dhcp-server restart)

# Check if gedit is running
ip=$(/sbin/ifconfig wlan0 | grep -oP "(?<=inet addr:).*?(?=Bcast)" | sed -r 's/ //g')

# Make sure our IP is set properly
if [ "$ip" != "192.168.2.1" ]
then
    echo "`date -u`: Interface went down!  Restarting! ($ip != 192.168.2.1)"
    sudo ifconfig wlan0 down
    sudo ifconfig wlan0 up
    sudo ifconfig wlan0 192.168.2.1
    sudo service hostapd restart
    sudo service isc-dhcp-server restart
    exit
fi

# Is the DHCPD server up?
if pgrep "dhcpd" > /dev/null
then
    # Do Nothing
    echo "" > /dev/null
else
    echo "`date -u`: DHCPD was down!  Restarting!"
    sudo ifconfig wlan0 192.168.2.1
    sudo service isc-dhcp-server restart
fi
