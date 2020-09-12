import subprocess
import logging
import json
import os


class Disks (object):
    def __init__(self):

        logging.info('get current disk')
        p = subprocess.run("lsblk -o name,label,kname,fstype,mountpoint,type,hotplug,path,size,fstype,fssize,fsused,fsuse% --json",
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise Exception(
                'DiskError', 'unable_to_get_disk: {}'.format(p.stderr.decode()))
        self.disks = json.loads(p.stdout.decode())
        self.disks = self.disks['blockdevices']

    def refresh_disks(self):
        """refresh the list of disks and their attributes
        """
        self.__init__()

    def check_disks_partitions(self, disk=None):
        """Execute check disk (fsck -va) on all disk if none is given.
        If disk is given this will execute fsck on this disk

        Keyword Arguments:
            disk {str} -- path of the disk, example: '/dev/sda' (default: {None})

        Raises:
            Exception: if check disk causes problems
        """
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
        """find disk by mountpoint or path

        Arguments:
            disk_to_find {str} -- path of the disk or partition, example: '/dev/sda' or '/dev/sda1' 

        Raises:
            Exception: [if disk is impossible to find]

        Returns:
            [dict] -- [dict that contains lsblk informations about disk or partition]
        """
        self.refresh_disks()

        for disk in self.disks:
            if disk['path'] == disk_to_find or disk_to_find == disk['mountpoint']:
                return disk

            if 'children' in disk.keys():
                for children in disk['children']:
                    if disk_to_find == children['path'] or disk_to_find == children['mountpoint']:
                        return children

        raise Exception('disk', 'unable_to_find_disk: {}'.format(disk_to_find))

    def mount_disk(self, disk_to_mount, mount_point=None):
        """mount disk given in parameters on mount point. 
        if mount point is given: disk will be mounted on it
        if not : disk will be mounted on /media/<name of disk>

        Arguments:
            disk_to_mount {str} -- path of disk like '/dev/sda

        Keyword Arguments:
            mount_point {str} -- path on mount point like '/media/mount' (default: {None})

        Raises:
            Exception: given disk is unknow
            Exception: mount operation is impossible

        Returns:
            [type] -- [description]
        """
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
        """umount given disk

        Arguments:
            disk_to_umount {str} -- path or mount point of disk (/media/sda or /dev/sda)

        Raises:
            Exception: given disk is unknow
            Exception: mount operation is impossible

        Returns:
            bool -- True if umount operation is ok
        """
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
        """return only usb disk : disk with hotplug flag is True 

        Returns:
            list -- list of disk and attributes of hotplug disk
        """

        self.refresh_disks()
        ret = list()
        for disk in self.disks:
            if 'sd' in disk['name'] and disk['hotplug'] is True:
                ret.append(disk)
        return ret

    def check_read_and_write_disk_performance(self, disk):
        """check wrinting and reading performance on given disk by writing and reading a 1GB generated image

        Arguments:
            disk {str} -- path of the disk, example: '/dev/sda'

        Raises:
            Exception: if writing on disk is impossible
            Exception: if reading on disk is impossible

        Returns:
            dict -- performance of writing and reading of given disk
        """
        self.mount_disk(disk)
        mount_point = self.find_disk(disk)['mountpoint']

        perf = dict()

        p = subprocess.run("sudo dd count=1000 bs=1M if=/dev/zero of={}/test.img".format(mount_point),
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise Exception(
                'DiskError', 'unable_to_test_read_performance: {}'.format(p.stderr.decode()))

        temp = p.stderr.decode()
        perf['write']=temp.splitlines()[-1]

        # Free buffer
        self.umount_disk(disk)
        self.mount_disk(disk)
        
        mount_point = self.find_disk(disk)['mountpoint']

        p = subprocess.run("sudo dd count=1000 bs=1M if={}/test.img of=/dev/null".format(mount_point),
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if p.returncode != 0:
            raise Exception(
                'DiskError', 'unable_to_test_write_performance: {} '.format(p.stderr.decode()))
        
        temp = p.stderr.decode()
        perf['read'] = temp.splitlines()[-1]
        p = subprocess.run("sudo sudo rm {}/test.img".format(mount_point),
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return perf

    def check_disk_capacity_performance_errors(self, disk):
        self.umount_disk(disk)
        self.format_disk(disk, 'ext4')
        mount_point = self.mount_disk(disk)
        p = subprocess.Popen([" sudo f3write {}  ".format(
            mount_point)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        print (p.stdout.decode())
        if p.poll() is not None:
            raise Exception(
                'DiskError', 'unable_to_shred_disk: {}'.format(p.stderr))
        p = subprocess.Popen([" sudo f3read {} > /tmp/f3read.txt ".format(
            mount_point)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        print (p.stdout.decode())


    def format_disk(self, disk, fstype):
        """format the disk with given fs type

        Arguments:
            disk {str} -- path of the disk, example: '/dev/sda' 
            fstype {str} -- type of filesystem, example: 'ext4'

        Raises:
            Exception: formating disk is impossible
        """
        self.refresh_disks()
        temp_disk = self.find_disk(disk)
        p_format = subprocess.run("sudo mkfs -F -t {} {}".format(fstype, disk),
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p_format.returncode != 0:
            raise Exception('DiskError', 'unable_to_format_disk: {} {}'.format(
                disk, p_format.stderr.decode()))

    def shred_disks(self, disk):

        self.refresh_disks()
        self.umount_disk(disk)

        p = subprocess.Popen(["sudo shred -n 1 -v -z {} 2> /tmp/shred.txt & disown".format(
            disk)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if p.poll() is not None:
            raise Exception(
                'DiskError', 'unable_to_shred_disk: {}'.format(p.stderr))
        else:
            return p.pid

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
    # print(disk.format_disk('/dev/sda', 'ext4'))
    # print(disk.mount_disk('/dev/sda', '/media/sda'))
    # print(disk.umount_disk('/media/sda'))
    # print(disk.shred_disks('/dev/sda'))
    # print(disk.format_disk('/dev/sda', 'ext4'))
    print (disk.check_read_and_write_disk_performance('/dev/sdc'))
    print (disk.check_disk_capacity_performance_errors('/dev/sdc'))
