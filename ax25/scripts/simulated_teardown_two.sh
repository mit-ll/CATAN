# © 2015 Massachusetts Institute of Technology

#run with sudo

pkill ax25d
pkill kissattach
pkill socat
rm -f /var/lock/LCK..ttyUSB*

#axctl radio KI4SNH-2 KI4SNH-1 -kill
