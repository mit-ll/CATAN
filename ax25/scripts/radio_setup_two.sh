# © 2015 Massachusetts Institute of Technology

#run with sudo

ser1=/dev/ttyUSB0
ser2=/dev/ttyUSB1

python kiss_on.py $ser1
python kiss_on.py $ser2

kissattach $ser1 radio 192.168.3.10
kissattach $ser2 radio2 192.168.3.11
axparms -route add radio default
ax25d

#then run:
#watch -d "netstat --ax25"

#misc cmds
#ls /dev/ttyUSB*
#ls /var/lock/*
#axparms -route list
