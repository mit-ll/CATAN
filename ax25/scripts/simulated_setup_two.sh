# © 2015 Massachusetts Institute of Technology

#first set up serial ports

socat -d -d pty,raw,echo=0 pty,raw,echo=0 &
out=`lsof -c socat | grep -oP '/dev/pts/.*' | tail -n 2`

#run with sudo
#ser1=/dev/pts/5
#ser2=/dev/pts/6

#for each serial port, set the radio to KISS mode and call kissattach
i=1

for ser in $out
do
   python kiss_on.py $ser
   kissattach $ser radio$i 192.168.3.$((i+10))
   i=$((i+1))
done

#python kiss_on.py $ser1
#python kiss_on.py $ser2
#kissattach $ser1 radio 192.168.3.10
#kissattach $ser2 radio2 192.168.3.11

axparms -route add radio1 default
ax25d

#ls /dev/ttyUSB*
#ls /var/lock/*
#ifconfig
#axparms -route list
