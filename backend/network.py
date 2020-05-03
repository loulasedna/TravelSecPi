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
        p = subprocess.run("sudo ip link set {} up".format(
            interface), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.stdout.decode() if p.returncode == 0 else p.stderr.decode()

    def deactivate_interface(self, interface):
        p = subprocess.run("sudo ip link set {} down".format(
            interface), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.stdout.decode() if p.returncode == 0 else p.stderr.decode()

    def activate_nat(self, interface_in, interface_out):
        pass

    def deactivate_nat(self, interface_in, interface_out):
        pass

    def check_internet_connection(self):
        check = dict()
        check['default_gw'] = False
        check['default_ping'] = False
        check['dns'] = False
        check['internet_ping'] = False
        check['http'] = False
        check['https'] = False

        # check if default route
        process = subprocess.run(
            "ip route show default", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if 'default' in process.stdout.decode():
            check['default_gw'] = True
            gw = process.stdout.decode().split(' ')[2]
            self.interfaces['default_interface'] = process.stdout.decode().split(' ')[
                4]
        else:
            return check

        # check ping default_gateway
        process = subprocess.run(
            "ping -c 1 {}".format(gw), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode == 0:
            check['default_ping'] = True

        # check if name resolution is ok
        process = subprocess.run(
            "host google.com", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode == 0:
            check['dns'] = True
        else:
            return check

        # check if ping google is OK
        process = subprocess.run(
            "ping -c 1 www.google.com", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode == 0:
            check['internet_ping'] = True

        # check http
        process = subprocess.run("wget http://www.google.com --timeout=2 --tries=2 -O  /dev/null",
                                 shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode == 0:
            check['http'] = True

        # check https
        process = subprocess.run("wget https://www.google.com --timeout=2 --tries=2 -O  /dev/null",
                                 shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode == 0:
            check['https'] = True

        return check

    def get_internet_speed(self):
        p = subprocess.run("speedtest-cli --json", shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return p.stdout.decode() if p.returncode == 0 else p.stderr.decode()


class wifi_interfaces(network):
    def __init__(self):
        self.wifilist = dict()

    def scan_wifi(self, wifi_interfaces):
        wifi_interfaces = list(wifi_interfaces)
        scan = dict()
        for wifi_interface in wifi_interfaces:

            self.activate_interfaces(wifi_interface)

            process = subprocess.run("sudo iw {} scan".format(
                wifi_interface), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if process.returncode != 0:
                raise Exception()

            item = None
            lines = process.stdout.decode().splitlines()
            for line in lines:

                if re.search(r"[a-z0-9:]{17}", line):  # MAC/interface/BSS

                    scan[item['interface']].append(
                        item) if item is not None else None  # add dict only if created -> after

                    item = dict()  # create new dict for new wifi

                    item['mac'] = False
                    item['wpa'] = False
                    item['wpa2'] = False
                    item['tkip'] = False
                    item['ccmp'] = False
                    item['psk'] = False
                    item['wep'] = False

                    split_line = line.split(' ')
                    item['interface'] = split_line[2].split(')')[0]
                    item['BSS'] = split_line[1].split('(')[0]
                    if item['interface'] not in scan.keys():
                        scan[item['interface']] = list()

                if 'signal:' in line:
                    item['power'] = line.split(' ')[-2]
                if 'freq:' in line:
                    item['freq'] = line.split(' ')[-1]
                if 'SSID:' in line:
                    item['ssid'] = line.split(' ')[-1]
                if 'WPA:' in line:
                    item['wpa'] = True
                if 'RSN:' in line:
                    item['wpa2'] = True
                if 'WEP:' in line:
                    item['wep'] = True
                if 'CCMP' in line:
                    item['ccmp'] = True
                if 'TKIP' in line:
                    item['tkip'] = True
                if 'PSK' in line:
                    item['psk'] = True
        self.wifilist = scan
        return scan

    def connect_wifi(self,wifiname, password):

       
        if wifi['wpa'] is True and wifi['wpa2'] is True:
            print ('wpa2')
        if wifi['wpa'] is True and wifi['wpa2'] is False:
            print ('wpa1')
        if wifi['wep'] is True:
            print ('wep')
        if wifi['wep'] is False and wifi['wpa'] is False and wifi['wpa2'] is False:
            print ('no cipher')
        pass

    def disconnect_wifi(self, wifi_interface):
        process = subprocess.run("sudo iw {} disconect".format(
            wifi_interface), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if process.returncode != 0:
            raise Exception()


class ethernet_interfaces(network):
    def list_interfaces(self):
        pass


if __name__ == "__main__":
    wifi = wifi_interfaces()
    print(wifi.get_interfaces())
    print(wifi.scan_wifi(['wlan0', 'wlan1']))
    print(wifi.get_internet_speed())
    print(wifi.check_internet_connection())
    
    
    a = {'wlan0': [{'mac': False, 'wpa': False, 'wpa2': True, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': '00:13:ef:f3:06:c4', 'freq': '2412', 'power': '-34.00', 'ssid': 'Renagre-Nippon'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': '00:37:b7:07:f9:0e', 'freq': '2412', 'power': '-32.00', 'ssid': 'Renagre-bgn'}, {'mac': False, 'wpa': False, 'wpa2': False, 'tkip': False, 'ccmp': False, 'psk': False, 'wep': False, 'interface': 'wlan0', 'BSS': 'c0:c1:c0:59:c4:ed', 'freq': '2437', 'power': '-27.00', 'ssid': '\\x00\\x00\\x00\\x00\\x00\\x00'}, {'mac': False, 'wpa': True, 'wpa2': False, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': 'ca:09:c9:fe:2c:50', 'freq': '2467', 'power': '-34.00', 'ssid': 'freebox_Adrien'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': '00:37:b7:07:f9:0f', 'freq': '5180', 'power': '-60.00', 'ssid': 'Renagre-bgn_5GHz'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': '6c:38:a1:05:9b:7d', 'freq': '5180', 'power': '-81.00', 'ssid': 'Bbox-E5221EED'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': 'ac:3b:77:4d:c9:0d', 'freq': '5180', 'power': '-59.00', 'ssid': 'SFR-c906_5GHz'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': '84:a1:d1:2d:1a:84', 'freq': '5680', 'power': '-67.00', 'ssid': 'Bbox-AF9F8D9C'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': 'ac:3b:77:4d:c9:0c', 'freq': '2412', 'power': '-34.00', 'ssid': 'LamaFiesta'}, {'mac': False, 'wpa': True, 'wpa2': False, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': 'c2:c1:c0:59:c4:ee', 'freq': '2437', 'power': '-25.00', 'ssid': 'dd-wrt_vap2'}, {'mac': False, 'wpa': False, 'wpa2': False, 'tkip': False, 'ccmp': False, 'psk': False, 'wep': False, 'interface': 'wlan0', 'BSS': 'c0:c1:c0:59:c4:ed', 'freq': '2437', 'power': '-33.00', 'ssid': 'dd-wrt'}, {'mac': False, 'wpa': False, 'wpa2': False, 'tkip': False, 'ccmp': False, 'psk': False, 'wep': False, 'interface': 'wlan0', 'BSS': 'c2:c1:c0:59:c4:ef', 'freq': '2437', 'power': '-25.00', 'ssid': 'dd-wrt_vap3'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan0', 'BSS': '6c:38:a1:05:9b:7c', 'freq': '5180', 'power': '-77.00', 'ssid': ''}], 'wlan1': [{'mac': False, 'wpa': True, 'wpa2': True, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan1', 'BSS': '00:37:b7:07:f9:0f', 'freq': '5180', 'power': '-65.00', 'ssid': 'Renagre-bgn_5GHz'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan1', 'BSS': '84:a1:d1:2d:1a:84', 'freq': '5680', 'power': '-70.00', 'ssid': 'Bbox-AF9F8D9C'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan1', 'BSS': '00:37:b7:07:f9:0e', 'freq': '2412', 'power': '-50.00', 'ssid': 'Renagre-bgn'}, {'mac': False, 'wpa': False, 'wpa2': True, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan1', 'BSS': '00:13:ef:20:3d:38', 'freq': '2412', 'power': '-50.00', 'ssid': 'Renagre-USA'}, {'mac': False, 'wpa': False, 'wpa2': False, 'tkip': False, 'ccmp': False, 'psk': False, 'wep': False, 'interface': 'wlan1', 'BSS': 'c0:c1:c0:59:c4:ed', 'freq': '2437', 'power': '-24.00', 'ssid': 'dd-wrt'}, {'mac': False, 'wpa': False, 'wpa2': False, 'tkip': False, 'ccmp': False, 'psk': False, 'wep': False, 'interface': 'wlan1', 'BSS': 'c2:c1:c0:59:c4:ef', 'freq': '2437', 'power': '-24.00', 'ssid': 'dd-wrt_vap3'}, {'mac': False, 'wpa': True, 'wpa2': False, 'tkip': False, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan1', 'BSS': 'c2:c1:c0:59:c4:ee', 'freq': '2437', 'power': '-24.00', 'ssid': 'dd-wrt_vap2'}, {'mac': False, 'wpa': True, 'wpa2': True, 'tkip': True, 'ccmp': True, 'psk': True, 'wep': False, 'interface': 'wlan1', 'BSS': 'ac:3b:77:4d:c9:0c', 'freq': '2412', 'power': '-56.00', 'ssid': 'LamaFiesta'}]}
    for element in a:
        wifi.connect_wifi(element,'password')

        
        
    # https://donnutcompute.wordpress.com/2014/04/20/connect-to-wi-fi-via-command-line/
