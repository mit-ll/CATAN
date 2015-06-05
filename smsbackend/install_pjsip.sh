#!/bin/bash
#
# Author: Hongyi Hu
# © 2015 Massachusetts Institute of Technology
# Warning: The PJProject is unfortunately very finicky
# and will die if certain things are misconfigured.

# Download dependencies
printf "Downloading dependencies . . .\n"
sudo apt-get install python-dev

# Download pjproject source
printf "Downloading pjproject source . . .\n"
wget http://www.pjsip.org/release/2.3/pjproject-2.3.tar.bz2
tar jxvf pjproject-2.3.tar.bz2
rm pjproject-2.3.tar.bz2
sudo mv pjproject-2.3 /opt/catan/pjproject-2.3
sudo chown pi.pi /opt/catan/pjproject-2.3
cd /opt/catan/pjproject-2.3

printf "Configuring . . .\n"

# config_site.h
mkdir -p pjlib/pj

cat <<EOF > pjlib/pj/config_site.h
#define PJMEDIA_AUDIO_DEV_HAS_PORTAUDIO 0
#define PJMEDIA_AUDIO_DEV_HAS_ALSA 1
#include <pj/config_site_sample.h>
EOF

# Configure for linux
export CFLAGS="$CFLAGS -fPIC"
chmod +x configure
./configure

make dep
make

printf "Building python bindings\n"
cd pjsip-apps/src/python
sudo make
sudo make install

printf "Installing the SMS backend as a service\n"
sudo cp catan_sms /opt/catan/bin/catan_sms
sudo cp catan_sms_service.sh /etc/init.d/catan_sms
sudo update-rc.d catan_sms defaults
sudo /etc/init.d/catan_sms start
