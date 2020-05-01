import subprocess
import logging
import json


class Disks (object):
    def __init__(self):
        self.disks = None

    def refresh_disks(self):
        try:
            p = subprocess.run("lsblk -o name,label,kname,fstype,mountpoint --json",
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = p.stdout.decode()
            stderr = p.stderr.decode()
            self.disks = json.loads(stdout)
        except Exception as e:
            logging.debug(e, stderr)

    def check_disks_partitions(self, disk=None):
        if self.disks is None:
            return None
        elif disk is None:
            for disk in self.disks['blockdevices']:
                if 'sd' in disk['name']:
                    for partition in disk['children']:
                        p = subprocess.run("sudo fdisk -va %s".format(
                            partition['name']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout = p.stdout.decode()
                        stderr = p.stderr.decode()

    def mount_disks(self, disks=disk, label=label):
        p = subprocess.run(" %s %s".format(
            disk, label), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.stdout.decode()
        stderr = p.stderr.decode()
        pass

    def umount_disks(self, disks=None):

        pass

    def view_usb_disks(self):
        pass

    def check_disks_hardware(self, disks=None):
        pass

    def check_disk_read_performance(self, disk=None):
        # check if disk is mounted
        # checl if disk is like /dev/sda or disk1
        p = subprocess.run("dd count=1000 bs=1M if=/dev/urandom of=test.img",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.stdout.decode()
        stderr = p.stderr.decode()

    def check_disk_write_performace(self, disk=None):
        p = subprocess.run("dd count=1000 bs=1M if=test.img of=/dev/null",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.stdout.decode()
        stderr = p.stderr.decode()

    def check_disk_errors(self, disks=None):
        pass

    def format_disks(self, disks=None, type=type):

        p = subprocess.run("",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.stdout.decode()
        stderr = p.stderr.decode()

        pass

    def shred_disks(self, disks=None):
        self.umount_disks(disks=disks)
        p = subprocess.run("sudo shred -n 1 -v -z %s".format(disks),
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = p.stdout.decode()
        stderr = p.stderr.decode()
        pass

    def create_luks_disks(self, disks=None):
        pass


if __name__ == "__main__":
    disk = Disks()
    disk.refresh_disks()
