# © 2015 Massachusetts Institute of Technology

#run with sudo

pkill ax25d
pkill kissattach
rm -f /var/lock/LCK..ttyUSB*

#axctl    (to kill ax25 network connections)
#sudo axctl radio KI4SNH-2 KI4SNH-1 -kill
