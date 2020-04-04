#First working version v1.0

import subprocess
import time

class Backup:
    def __init__(self):
        self.backup_from = "/home/"
        self.backup_to = "/opt/scripts/new_backup/RemoteBackup/_HOST_BACKUPS/RaspberryPi3"
        self.backup_name = "NEW-BACKUP-RPi3.tar.gz"
        self.move_to = None
        self.backup_script_folder = None
        self.backup_log = None
        self.do_backup = None
        self.ping_counter = 100
        self.do_shutdown = False
        self.mac_address_of_nas = "48:0f:cf:33:e3:aa"

    def start_nas(self):
        print("Open Media Vault (OMV) is starting...")
        exit_code = subprocess.call("wakeonlan "+ self.mac_address_of_nas, shell=True)
        if exit_code == 0:
            print("OMV has been started!")
        else:
            print("Error {} during starting OMV!".format(exit_code))

    def compress_folders(self):
        print("Executing LOCAL backup process...")
        exit_code = subprocess.call("sudo tar -czf " + self.backup_to+self.backup_name + " /home/pi/*", shell=True)
        if exit_code == 0:
            print("Compression is DONE!")
        else:
            print("Compression exited with error {}".format(exit_code))

    def pinger(self):
        print("Waiting for OMV to bootup...")
        while self.ping_counter > 0:
            exit_code = subprocess.call("ping -c 1 10.0.2.1", shell=True)
            self.ping_counter -= 1
            if exit_code == 0:
                print("OMV is ONLINE!")
                break
            elif exit_code == 1:
                print("OMV is still not online...")
                time.sleep(4)
            else:
                print("Error {} occurred!".format(exit_code))

    def mount_network_drive(self):
        map_folder = "/opt/scripts/new_backup/RemoteBackup"
        print("Mounting NAS to "+map_folder)
        subprocess.call("mount.cifs -v //10.0.2.1/Backup " + map_folder + " -o user=Foklan,password=adM1n*72506187K", shell=True)
        print("Network drive has been mounted!")

    def move_zip_to_nas(self):
        print("Moving compressed file to NAS...")
        exit_code = subprocess.call("sudo mv -f " + self.backup_to+self.backup_name + " " + self.backup_to)
        if exit_code == 0:
            print("Backup was successfully moved!")
        else:
            print("Error {} occurred!".format(exit_code))

    def start(self):
        self.start_nas()
        self.compress_folders()
        self.pinger()
        self.mount_network_drive()
        self.move_zip_to_nas()

    def shutdown_nas(self):
        pass

backup = Backup()
backup.start()