#!/bin/bash

echo "begin installation"

echo "update system"
sudo apt-get -y update
sudo apt-get -y dist-upgrade

echo "install base packets"
sudo apt-get install -y exfat-fuse exfat-utils ntfs-3g usbmount

echo "install packet for cypher disk"
sudo apt-get install -y ecryptfs-utils cryptsetup

echo "install vpn and network utilities"
sudo apt-get install -y openvpn wireguard-tools strongswan iodine

echo "install network utilities"
sudo apt-get install -y  nmap tcpdump arping dnsutils iw aircrack-ng hostapd stubby tor

echo "install backup utilities"
sudo apt-get install -y rsync restic

echo "install restore files utilities"
sudo apt-get install -y testdisk

echo "purge system"
sudo apt-get -y autoclean
sudo apt-get -y autoremove
