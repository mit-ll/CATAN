#!/bin/sh -e
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


[ -f "/etc/supervisor/conf.d/catan_webserver.conf" ] && rm /etc/supervisor/conf.d/catan_webserver.conf
supervisorctl stop catan_webserver
supervisorctl reread
supervisorctl update
