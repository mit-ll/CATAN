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

These instructions should help you get a CATAN node up and running.

## Raspberry Pi
1. Setup your raspberry pi with Raspbian and get it on the internet. [Guide](http://www.raspberrypi.org/documentation/installation/installing-images/)
 * We provide a script to help copy the image over in *raspberry-pi*.
 
2. Run **raspi-config** on the Pi and expand the file system and enable SSH.
	* **1 Expand File System**
	* **9 Advanced Options**
		* **A4 SSH**
		* **\<Enable\>**
	* Exit, and reboot system.
3. Ensure that the Pi is connected to the internet (and that you are connecting over **eth0** for the initial setup).
4. Run our setup script from another machine.  This should install all dependencies and services for CATAN. The CATAN Node id cannot be zero. 
```bash
	./setup_new_pi.sh <ip address of pi> <CATAN Node ID>
```

*Note: This install has only been tested and confirmed on Rasbian Jessie.*

### Raspberry Pi USB Configuration
             ______ ______
     _____  | USB0 | USB2 |
    | ETH | | USB1 | USB3 |
    -----------------------

*  ETH - Ubiquiti Rocket M2 Router
* USB0 - Internet USB/Ethernet Dongle
* USB1 - OpenBTS USB/Ethernet Dongle
* USB2 - USB Extender to GPS
* USB3 - Wi-Fi Frontend card

    
### Raspberry Pi Settings

 - Username/Password: pi/raspberry
 - IP Address for OpenBTS port: 192.168.0.3
 - IP Address for WiFi interface: 192.168.2.1
 - Internet should be DHCP, may require a restart
 - UART: 
```bash
	screen /dev/ttyUSB<Number that Pi is on> 115200
```
![UART Image](http://workshop.raspberrypiaustralia.com/assets/console-cable-connections.jpg)

## Router Firmware


 1. Connect your computer to the router and ensure that it receives and IP address over DHCP (10.X.X.X subnet).
 2. Flash the appropriate [Broadband-Hamnet](http://www.broadband-hamnet.org/) firmware onto the router, found in *router_firmware*. For example (ubiquiti_rocket2)

 ```bash
$ ./flash_ubiquiti.sh
```
 3. Then configure the router ID to the corresponding CATAN node ID (This requires a HAM radio license and callsign).

 ```bash
$ ./config_ubiquiti.sh
```
[More detailed instructions in the router_software file](https://github.com/mit-ll/CATAN/tree/master/router_software/ubiquiti_rocket2)

# Debugging

## WiFi Problems
 * Check to make sure that both hostapd and dhcpd are running:
 ```bash
$ ps aux | grep hostapd
root       803  0.4  0.2   5912  2680 ?        Ss   20:48   0:02 /usr/sbin/hostapd -B -P /run/hostapd.pid /etc/hostapd/hostapd.conf

$ ps aux | grep dhcpd
root      2354  0.0  0.7  10488  7352 ?        Ss   20:58   0:00 /usr/sbin/dhcpd -q -cf /etc/dhcp/dhcpd.conf -pf /var/run/dhcpd.pid wlan0
 ```


# Useful links

- [Connecting to Pi using FTDI](http://workshop.raspberrypiaustralia.com/usb/ttl/connecting/2014/08/31/01-connecting-to-raspberry-pi-via-usb/)

# Installing as a service

- [Link](http://blog.scphillips.com/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/)

# Citation

Please use this DOI number reference, published on [Zenodo](https://zenodo.org), when citing the software:    
[![DOI](https://zenodo.org/badge/36947912.svg)](https://zenodo.org/badge/latestdoi/36947912)

# Disclaimer
DISTRIBUTION STATEMENT A. Approved for public release: distribution unlimited.  

<b>© 2019 MASSACHUSETTS INSTITUTE OF TECHNOLOGY</b>  
* Subject to FAR 52.227-11 – Patent Rights – Ownership by the Contractor (May 2014)  
* SPDX-License-Identifier: BSD-3-Clause    

This material is based upon work supported by the Air Force under Air Force Contract No. FA8721-05-C-0002. Any opinions, findings, conclusions or recommendations expressed in this material are those of the author(s) and do not necessarily reflect the views of the Air Force.

The software/firmware is provided to you on an As-Is basis

## How to test:
* You should be able to see CATAN services running with 
```bash
$ ps aux | grep catan. 
```
 * Also, the /opt/catan folder will include all of the runtime files for CATAN. Logs are stored in /opt/catan/log.

 * After you have two nodes running (each with its own radio) you can double check that the radios see each other by 
 going to localnode:8080. In the main panel go to Mesh Status- you should be able to see the other node's radio 
 under current neighbors. 
