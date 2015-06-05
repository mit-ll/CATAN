# © 2015 Massachusetts Institute of Technology

#run with sudo
myusername=`whoami`
if [ $myusername != 'root' ]
then
  echo "You should probably run with sudo"
  exit 1
else
  echo "running as root"
fi

#get name of serial device
if [ $# -ge 1 ]
then
  ser1=$1
else
  ser1=/dev/ttyUSB0
fi
echo "using $ser1 as serial port"

python kiss_on.py $ser1
if [ $? -ne 0 ]
then
  echo "ERROR: Setting KISS mode failed"
  exit 1
fi



