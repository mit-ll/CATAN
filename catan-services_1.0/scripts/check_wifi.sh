# © 2015 Massachusetts Institute of Technology
ifconfig mon.wlan0 >/dev/null || (sudo service hostapd restart && sudo service isc-dhcp-server restart)

