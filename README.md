                          .g8"""bgd     db   MMP""MM""YMM   db      `7MN.   `7MF'
                        .dP'     `M    ;MM:  P'   MM   `7  ;MM:       MMN.    M  
                        dM'       `   ,V^MM.      MM      ,V^MM.      M YMb   M  
                        MM           ,M  `MM      MM     ,M  `MM      M  `MN. M  
                        MM.          AbmmmqMA     MM     AbmmmqMA     M   `MM.M  
                        `Mb.     ,' A'     VML    MM    A'     VML    M     YMM  
                          `"bmmmd'.AMA.   .AMMA..JMML..AMA.   .AMMA..JML.    YM  
                                                        
                        Communication Assistance Technology over Ad-Hoc Networks
                         
                         
# Overview

CATAN is an emergency communication system that can be deployed
without other supporting infrastructure to assist an affected
population report status information, receive information about the
status of others, and communicate with relief personnel following a
disaster.  CATAN supplements existing tools such as Google Person
Finder by providing a direct method of collecting and transmitting
volunteered data from an affected site suffering a loss in
connectivity.

CATAN is designed to bridge multiple wireless communication
technologies using a mesh of portable "nodes".  The nodes provide a
web based user interface through Wi-Fi radios and (optionally) GPRS
radios.  They can optionally be configured to provide an SMS based
user interface.  The user interface allows users to report a basic set
of status information that would be relevant to connecting with loved
ones and assisting disaster responders.  The nodes synchronize
information via a custom peer-to-peer networking protocol.  CATAN is
designed to be agnostic to the data link used to communicate between
peer nodes.  The current implementation includes code to utilize UDP
packets over a peer-to-peer Wi-Fi mesh network.  It also provides code
to link the nodes via amateur radios using the AX25 protocol.  In
order to disseminate information beyond the peer-to-peer network,
CATAN provides the ability for a gateway node that has access to the
Internet to upload data to an instance of Google Person Finder.

The core CATAN services are written in Python and designed to run in
Linux on a Raspberry Pi device.  The web base front end is written in
PHP and also runs on the Raspberry Pi.  The CATAN project includes
software that augments the Wi-Fi router firmware (provided by the
Broadband-Hamnet) to allow network flooding and code that interacts
with OpenBTS to implement the SMS interface Also included are design
files for 3D printing an enclosure for the node components.

The advantage of CATAN is its use of commodity off the shelf
components to provide an emergency communication infrastructure at a
minimal cost.  It is designed to interoperate with the wireless
communication devices that survivors of a disaster are likely to have
access to.  This type of technology should be of interest to the
humanitarian assistance and disaster response (HADR) community.

For more information check out our [presentation](https://www.youtube.com/watch?v=mckd1VZACb8) at ICCM 2014 or [publication](http://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=7343958) at GHTC 2015.

Email: catan@ll.mit.edu

# Installation Instructions

1. Setup your raspberry pi with Raspbian and get it on the internet. [Guide](http://www.raspberrypi.org/documentation/installation/installing-images/)
 * We provide a script to help copy the image over in *raspberry-pi*.
 
2. Run **raspi-config** on the Pi and expand the file system and enable SSH.
	* **1 Expand File System**
	* **9 Advanced Options**
		* **A4 SSH**
		* **\<Enable\>**
	* Exit, and reboot system.
3. Ensure that the Pi is connected to the internet (and that you are connecting over **eth0** for the initial setup).
4. Run our setup script.  This should install all dependencies and services for CATAN.
```bash
	./setup_new_pi.sh <ip address> <CATAN Node ID>
```

*Note: This install has only been tested and confirmed on Rasbian Jessie.*

# Raspberry Pi USB Configuration
             ______ ______
     _____  | USB0 | USB2 |
    | ETH | | USB1 | USB3 |
    -----------------------

*  ETH - Ubiquiti Router
* USB0 - Internet USB/Ethernet Dongle
* USB1 - OpenBTS USB/Ethernet Dongle
* USB2 - USB Extender to GPS
* USB3 - Wi-Fi Frontend card

# Raspberry Pi Settings

 - Username/Password: pi/raspberry
 - IP Address for OpenBTS port: 192.168.0.3
 - IP Address for WiFi interface: 192.168.2.1
 - Internet should be DHCP, may require a restart
 - UART: 
```bash
	screen /dev/ttyUSB\<Number that Pi is on\> 115200
```

# Useful links

- [Connecting to Pi using FTDI](http://workshop.raspberrypiaustralia.com/usb/ttl/connecting/2014/08/31/01-connecting-to-raspberry-pi-via-usb/)

# Installing as a service

- [Link](http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/)

# Disclaimer
<p align="center">
This work was sponsored by the Department of the Air Force under Air
Force Contract #FA8721-05-C-0002.  Opinions, interpretations,
conclusions and recommendations are those of the authors and are not
necessarily endorsed by the United States Government.
<br>
© 2015 Massachusetts Institute of Technology 
</p>
