import subprocess
import logging
import json
import os


class Disks (object):
    def __init__(self):
        p = subprocess.run("lsblk -o name,label,kname,fstype,mountpoint,type,hotplug,path,size,fstype,fssize,fsused,fsuse% --json",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise Exception(
                'DiskError', 'unable_to_get_disk: {}'.format(p.stderr.decode()))
        self.disks = json.loads(p.stdout.decode())
        self.disks = self.disks['blockdevices']

    def refresh_disks(self):
        self.__init__()

    def check_disks_partitions(self, disk=None):
        self.refresh_disks()
        if disk is None:
            for disk in self.disks:
                if 'sd' in disk['name']:
                    for partition in disk['children']:
                        p = subprocess.run("sudo fsck -a {} ".format(
                            partition['name']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if p.returncode != 0:
                            raise Exception(
                                'DiskError', 'unable_to_check_disk: {} '.format(disk))

    def find_disk(self, disk_to_find):
        self.refresh_disks()

        for disk in self.disks:
            if disk['path'] == disk_to_find or disk_to_find == disk['mountpoint']:
                return disk

            if 'children' in disk.keys():
                for children in disk['children']:
                    if disk_to_find == children['path'] or disk_to_find == children['mountpoint']:
                        return children

    def mount_disk(self, disk_to_mount, mount_point=None):
        if mount_point is None:
            mount_point = '/media/'+disk_to_mount.split('/')[-1]

        temp = self.find_disk(disk_to_mount)
        print(temp)

        if temp['mountpoint'] == mount_point:
            return True

        if temp is None:
            raise Exception(
                'disk', 'unable_to_find_disk: {}'.format(disk_to_mount))

        if temp['mountpoint'] is not None:
            return temp['mountpoint']
        else:
            mount = subprocess.run("pmount {} {} ".format(
                disk_to_mount, mount_point), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if mount.returncode != 0:
                raise Exception(
                    'DiskError', 'unable_to_mount_disk: {} {} '.format(disk_to_mount, mount_point))
            else:
                self.refresh_disks()
                return mount_point

    def umount_disk(self, disk_to_umount):

        temp = self.find_disk(disk_to_umount)
        print(disk_to_umount, temp)

        if temp is None:
            raise Exception(
                'disk', 'unable_to_find_disk: {}'.format(disk_to_umount))

        if temp['mountpoint'] is None:
            return True

        umount = subprocess.run("sudo pumount {}".format(
            disk_to_umount), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if umount.returncode != 0:
            raise Exception(
                'DiskError', 'unable_to_umount_disk: {} {}'.format(disk_to_umount, umount.stderr.decode()))
        else:
            self.refresh_disks()
            return True

    def view_usb_disks(self):
        self.refresh_disks()
        ret = list()
        for disk in self.disks:
            if 'sd' in disk['name'] and disk['hotplug'] is True:
                ret.append(disk)
        return ret

    def check_disk_read_performance(self, disk):
        # check if disk is mounted
        # check if disk is like /dev/sda or disk1
        self.mount_disk(disk)
        p = subprocess.run("dd count=1000 bs=1M if=/dev/urandom of=test.img",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise Exception(
                'DiskError', 'unable_to_test_read_performance: {}'.format(p.stderr.decode()))

    def check_disk_write_performace(self, disk=None):
        p = subprocess.run("dd count=1000 bs=1M if=test.img of=/dev/null",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise Exception(
                'DiskError', 'unable_to_test_write_performance: {} '.format(p.stderr.decode()))

    def check_disk_capacity_performance_errors(self, disk):
        # f3read & f3 write
        pass

    def format_disk(self, disk, type):
        self.refresh_disks()
        temp_disk = self.find_disk(disk)
        p_format = subprocess.run("sudo mkfs -F -t {} {}".format(type, disk),
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p_format.returncode != 0:
            raise Exception('DiskError', 'unable_to_format_disk: {} {}'.format(
                disk, p_format.stderr.decode()))

    def shred_disks(self, disk):
        """[summary]

        Arguments:
            disk {str} -- [disk to shred. Example '/dev/sda']

        Raises:
            Exception: [when it is impossible to shred the disk: disk name not correct...]

        Returns:
            [type] -- [True if shred is OK]
        """
        self.refresh_disks()
        self.umount_disk(disk)

        p = subprocess.Popen(["sudo shred -n 1 -v -z {} 2> /tmp/shred.txt & disown".format(
            disk)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print (p.poll())
        if p.poll() is not None:
            raise Exception(
                'DiskError', 'unable_to_shred_disk: {}'.format(p.stderr))
        else:
            return True

    def get_disk_usage(self, disk_name):
        ret = list()
        for disk in self.disks:
            temp = None
            if disk_name == disk['name'] or disk_name == disk['label']:
                temp = disk
            if 'children' in disk.keys():
                for children in disk['children']:
                    if disk_name == children['name'] or disk_name == children['label']:
                        temp = children
            if temp is not None:
                ret.append(dict(name=temp['name'],
                                size=temp['size'],
                                fssize=temp['fssize'],
                                fsused=temp['fsused'],
                                fsuse=temp['fsuse%'],
                                label=temp['label'],
                                path=temp['path']
                                ))
        return ret

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
    ret = disk.view_usb_disks()
    # print(disk.get_disk_usage('EOS_DIGITAL'))
    print(disk.format_disk('/dev/sda', 'ext4'))
    print(disk.mount_disk('/dev/sda', '/media/sda'))
    print(disk.umount_disk('/media/sda'))
    print(disk.shred_disks('/dev/sda'))
    print(disk.format_disk('/dev/sda', 'ext4'))
