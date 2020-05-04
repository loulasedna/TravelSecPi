import subprocess
import logging
import json


class Disks (object):
    def __init__(self):
        self.disks = None

    def refresh_disks(self):
            p = subprocess.run("lsblk -o name,label,kname,fstype,mountpoint --json",
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode !=0:
                raise Exception('DiskError','unable_to_check_disk: {} '.format(disk))

    def check_disks_partitions(self, disk=None):
        if self.disks is None:
            return None
        elif disk is None:
            for disk in self.disks['blockdevices']:
                if 'sd' in disk['name']:
                    for partition in disk['children']:
                        p = subprocess.run("sudo fdisk -va {} ".format(
                            partition['name']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if p.returncode !=0:
                            raise Exception('DiskError','unable_to_check_disk: {} '.format(disk))

    def mount_disks(self, disks=disk, label=label):
        p = subprocess.run("sudo mount {} {}".format(
            disk, label), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode !=0:
            raise Exception('DiskError','unable_to_mount_disk: {} on {}'.format(disks,label))

    def umount_disks(self, disks=None):
        p = subprocess.run("sudo umount {} {}".format(
            disk, label), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode !=0:
            raise Exception('DiskError','unable_to_mount_disk: {} on {}'.format(disks,label))
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
        if p.returncode !=0:
            raise Exception('DiskError','unable_to_test_read_performance')

    def check_disk_write_performace(self, disk=None):
        p = subprocess.run("dd count=1000 bs=1M if=test.img of=/dev/null",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode !=0:
            raise Exception('DiskError','unable_to_test_write_performance')

    def check_disk_errors(self, disks=None):
        pass

    def format_disks(self, disks=None, type=type):

        p = subprocess.run("",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
    def shred_disks(self, disks=None):
        
        self.umount_disks(disks=disks)
        
        p = subprocess.run("sudo shred -n 1 -v -z {}".format(disks),
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if p.returncode !=0:
                raise Exception('DiskError','unable_to_test_write_performance')
        
    def create_luks_disks(self, disks=None):
        
        """ 
        create 
        sudo cryptsetup --cipher aes-xts-plain64 --key-size 512 --hash sha512 --iter-time 2000 --align-payload=2048 -v luksFormat /dev/sda
        
        sudo cryptsetup luksOpen /dev/sda1 my_encrypted_volume
        Now you can mount it as usual:

        sudo mkdir /media/my_device
        sudo mount /dev/mapper/my_encrypted_volume /media/my_device
        To lock the container again, it needs to be unmounted first:

        sudo umount /media/my_device
        sudo cryptsetup luksClose my_encrypted_volume
        To automatically put it in the /media location, use the udisks tool

        sudo udisks --mount /dev/mapper/my_encrypted_volume """
        pass


if __name__ == "__main__":
    disk = Disks()
    disk.refresh_disks()
