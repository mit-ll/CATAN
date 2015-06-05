# Reference: http://wiki.openwrt.org/doc/howto/buildroot.exigence
# © 2015 Massachusetts Institute of Technology

sudo apt-get -y update
sudo apt-get -y install git-core build-essential
sudo apt-get -y install subversion

wget http://downloads.openwrt.org/kamikaze/7.09/brcm-2.4/OpenWrt-SDK-brcm-2.4-for-Linux-x86_64.tar.bz2
tar jxvf OpenWrt-SDK-brcm-2.4-for-Linux-x86_64.tar.bz2
mv OpenWrt-SDK-brcm-2.4-for-Linux-x86_64 openwrt-brcm-2.4

