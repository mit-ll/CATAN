#!/usr/bin/env bash

scriptPath=$(dirname $0)
cd $scriptPath

mkdir distribution
cp distribution/* .

cd catan-services_1.0
sudo debuild clean
yes | debuild -S -kcspensky@cs.ucsb.edu
sudo debuild clean
cd ..

mv *.deb distribution
mv *.build distribution
mv *.changes distribution
mv *.dsc distribution
mv *.tar.gz distribution

cd distribution/

for release in *.changes
do
  yes | debsign -kcspensky@cs.ucsb.edu $release
  yes | dput ppa:cspensky/catan $release
done
