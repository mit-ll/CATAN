#!/bin/sh -e
# © 2015 Massachusetts Institute of Technology

if [ -e "/etc/init.d/catan" ]; then
	echo "Uninstalling main service..."
        sudo /etc/init.d/catan stop
        sudo update-rc.d -f catan remove
        sudo unlink /etc/init.d/catan
fi

if [ -e "/etc/init.d/catan_dns" ]; then
	echo "Uninstalling DNS service..."
        sudo /etc/init.d/catan_dns stop
        sudo update-rc.d -f catan_dns remove
        sudo unlink /etc/init.d/catan_dns
fi

if [ -e "/etc/init.d/catan_gateway" ]; then
        echo "Uninstalling Gateway service..."
        sudo /etc/init.d/catan_gateway stop
        sudo update-rc.d -f catan_gateway remove
        sudo unlink /etc/init.d/catan_gateway
fi

