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
            logging.debug(e)

    def check_disks(self, disk=None):
        if self.disks is None:
            return None
        elif disk is None:
            for disk in self.disks['blockdevices']:
                if 'sd' in disk['name']:
                    for partition in disk['children']:
                        p = subprocess.run('sudo fdisk -va %s'.format(
                            partition['name']), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout = p.stdout.decode()
                        stderr = p.stderr.decode()


if __name__ == "__main__":
    disk = Disks()
    disk.refresh_disks()
    disk.check_disks()
