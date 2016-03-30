if [ $# -ne 2 ]
  then
    echo "Usage: $0 <raspbian image> <device (e.g., /dev/sdc)>"
	exit
fi

sudo dd bs=4M if=$1 of=$2
