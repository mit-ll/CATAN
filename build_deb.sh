mkdir distribution
cp distribution/* .

cd catan-services_1.0
sudo debuild clean
yes | debuild -uc -us
sudo debuild clean
cd ..

cd catan-nics-service_1.0
sudo debuild clean
yes | debuild -uc -us
sudo debuild clean
cd ..

mv *.deb distribution
mv *.build distribution
mv *.changes distribution
mv *.dsc distribution
mv *.tar.gz distribution

