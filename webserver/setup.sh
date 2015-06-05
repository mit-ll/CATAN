# Install apache2 and php
# © 2015 Massachusetts Institute of Technology
sudo -E apt-get install apache2 php5 libapache2-mod-php5 php5-dev php5-sqlite
sudo /etc/init.d/apache2 restart
if [ -d "/var/www/html" ]; then
	sudo ln -s $PWD/www /var/www/html/catan
else
	sudo ln -s $PWD/www /var/www/catan
fi


# Let's also try to use python
sudo -E apt-get install libapache2-mod-python
sudo a2enmod python
sudo a2enmod cgi
sudo service apache2 restart

# Setup a link to this our local file
sudo ln -s $PWD/cgi-bin/catan_script.py /usr/lib/cgi-bin/catan_script.cgi
sudo chown -h `whoami` /usr/lib/cgi-bin/catan_script.cgi
sudo chown -h `whoami` $PWD/cgi-bin/catan_script.py

sudo ln -s $PWD/cgi-bin/getMapData.py /usr/lib/cgi-bin/getMapData.cgi
sudo chown -h `whoami` /usr/lib/cgi-bin/getMapData.cgi
sudo chown -h `whoami` $PWD/cgi-bin/getMapData.py
