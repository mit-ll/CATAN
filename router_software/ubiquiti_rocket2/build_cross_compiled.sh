# © 2015 Massachusetts Institute of Technology

PATH=$PATH:${PWD}/openwrt/staging_dir/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/bin/
export PATH

STAGING_DIR=${PWD}/openwrt/staging_dir/toolchain-mips_34kc_gcc-4.8-linaro_uClibc-0.9.33.2/
export STAGING_DIR

mips-openwrt-linux-gcc ../src/broadcast_bridge.c -Wall -o broadcast_bridge_a71xxx
