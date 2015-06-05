# © 2015 Massachusetts Institute of Technology

PATH=$PATH:${PWD}/openwrt-brcm-2.4/staging_dir_mipsel/bin/
export PATH

STAGING_DIR=${PWD}/openwrt-brcm-2.4/staging_dir_mipsel/
export STAGING_DIR

mipsel-linux-gcc broadcast_bridge.c -Wall -o broadcast_bridge_brcm2.4




