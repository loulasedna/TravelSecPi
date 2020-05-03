import subprocess
import re
import json


class network(object):
    def __init__(self):
        self.interfaces = dict()
        self.interfaces['wired'] = dict()
        self.interfaces['wireless'] = dict()
        self.interfaces['loopback'] = dict()
        self.interfaces['other'] = dict()

        cmd = "ip -j link show"
        p = subprocess.run(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if p.returncode != 0:
            raise Exception()  # TODO

        interfaces = json.loads(p.stdout.decode())
        for interface in interfaces:
            interface_name = interface['ifname']
            if 'eth' in interface_name:
                self.interfaces['wired'][interface_name] = interface
            elif 'wl' in interface_name:
                self.interfaces['wireless'][interface_name] = interface
            elif 'lo' in interface['ifname']:
                self.interfaces['loopback'][interface_name] = interface
            elif 'tun' in interface['ifname']:
                self.interfaces['tunnel'][interface_name] = interface
            else:
                self.interfaces['other'][interface_name] = interface

    def refresh_interfaces(self):
        self.__init__()

    def get_interfaces(self):
        return self.interfaces

    def activate_interfaces(self, interface):
        p = subprocess.run("sudo ip link set %s up".format(
            interface), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.stdout.decode() if p.returncode == 0 else p.stderr.decode()

    def deactivate_interface(self):
        # sudo ip link set wlan0 down
        pass

    def activate_nat(self, interface_in, interface_out):
        pass

    def deactivate_nat(self, interface_in, interface_out):
        pass


class wifi_interfaces(network):

    def scan_wifi(self, wifi_interface):
        # scan = subprocess.run("sudo iw %s scan".format(
        #     wifi_interface),     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print(scan.returncode)

        # if scan.returncode != 0:
        #     raise Exception()

        # print(type(scan))
        pass

    def connect_wifi(self, wifi_interface, password):
        pass

    def disconnect_wifi(self, wifi_interface, password):
        pass


class ethernet_interfaces(network):
    def list_interfaces(self):
        pass


if __name__ == "__main__":
    # wifi = wifi_interfaces()
    # print(wifi.get_interfaces())
    # print(wifi.scan_wifi('wlan1'))
    scan = dict()
    item = None
    with open('example/iwscan.txt', 'r') as text:
        lines = text.readlines()

        for line in lines:

            if re.search(r"[a-z0-9:]{17}", line):  # MAC/interface/BSS

                scan[item['interface']].append(
                    item) if item is not None else None  # add dict only if created -> after 
                
                item = dict() # create new dict for new wifi
                
                item['mac'] = 'n'
                item['wpa'] = 'n'
                item['wpa2'] = 'n'
                item['tkip'] = 'n'
                item['ccmp'] = 'n'
                item['psk'] = 'n'

                split_line = line.split(' ')
                item['interface'] = split_line[2].split(')')[0]
                item['BSS'] = split_line[1].split('(')[0]
                if item['interface'] not in scan.keys():
                    scan[item['interface']] = list()

            if 'signal' in line:
                item['power'] = line.split(' ')[-2]
            if 'freq' in line:
                item['freq'] = line.split(' ')[-1].replace('\n', '')
            if 'SSID' in line:
                item['ssid'] = line.split(' ')[-1].replace('\n', '')
            if 'WPA:' in line:
                item['wpa'] = 'y'
            if 'RSN:' in line:
                item['wpa2'] = 'y'
            if 'WEP:' in line:
                item['wep'] = 'y'
            if 'CCMP' in line:
                item['ccmp'] = 'y'
            if 'TKIP' in line:
                item['tkip'] = 'y'
            if 'PSK' in line:
                item['psk'] = 'y'
        
        print (scan)