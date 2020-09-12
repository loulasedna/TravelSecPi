#! /bin/sh

echo 'update and upgrade'
sudo apt-get update && sudo apt-get -y dist-upgrade


#network tools

echo 'install network tools'
sudo apt-get install iw hostapd haveged nmap dnsmasq 

echo 'install dev tools'
sudo apt-get install python3-pip python-is-python3

echo 'install system tools'



