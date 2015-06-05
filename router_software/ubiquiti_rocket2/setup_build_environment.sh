# Reference: http://wiki.openwrt.org/doc/howto/buildroot.exigence
# © 2015 Massachusetts Institute of Technology

sudo apt-get -y update
sudo apt-get -y install git-core build-essential
sudo apt-get -y install subversion

git clone git://git.openwrt.org/openwrt.git
cd openwrt
./scripts/feeds update -a
./scripts/feeds install -a

make defconfig
make prereq
make menuconfig

make -j30 V=s
