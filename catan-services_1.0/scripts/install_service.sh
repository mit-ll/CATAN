sudo cp service_catan.sh /etc/init.d/catan
sudo update-rc.d catan defaults
sudo /etc/init.d/catan start

sudo cp service_dns.sh /etc/init.d/catan_dns
sudo update-rc.d catan_dns defaults
sudo /etc/init.d/catan_dns start

sudo cp service_gateway.sh /etc/init.d/catan_gateway
sudo update-rc.d catan_gateway defaults
sudo /etc/init.d/catan_gateway start

# Flask webserver
sudo cp catan_webserver.conf /etc/supervisor/conf.d/
supervisorctl reread
supervisorctl update
