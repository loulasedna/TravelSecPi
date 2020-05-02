class network(object):
    def __init__(self):
        pass

    def activate_interface(self):
        pass

    def deactivate_interface(self):
        pass

    def activate_nat(self, interface_in, interface_out):
        pass

    def deactivate_nat(self, interface_in, interface_out):
        pass


class wifi_connection(network):
    def __init__(self):
        pass

    def scan_wifi(self, wifi_interface):
        pass

    def connect_wifi(self, wifi_interface, password):
        pass

    def disconnect_wifi(self, wifi_interface, password):
        pass
