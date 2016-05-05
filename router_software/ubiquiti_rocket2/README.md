First connect the ubiquity M2 to your computer. It's powered over
 ethernet so either use a power injector or the power brick that 
 comes with some of the ubiquity hardware. 

 After connecting it to your computer, you should be able to go to 
 192.168.1.20 and see the admin panel come up. The username and pasword is ubnt.

Now go to http://www.broadband-hamnet.org/software-download.html and download 
the 3.0.0 version of the factory firmware for the Ubiquity Rocket M2

WARNING: if you don't have firmware version 5.5 or lower, you will brick your device if you 
try this. Check the version of firmware that your router is running under the main tab. If it is running 
version 5.6 then you will need to roll back the firmware version to 5.5.  This version is 
available from the manufacturer's website. Go to system update in the admin panel. 

When you have firmware version 5.5 or below, again go to the system update and now 
upload the 3.0.0 Factory firmware. 

After the update completes, you should be able to go to localnode:8080 and see 
a status page come up. The radio is still not configured- from a 
linux machine you must run the config_ubiquiti.sh in order to 
configure the radio to work with CATAN 
