#!/usr/bin/python3

from configparser import ConfigParser
import subprocess
import logging
import time
import os


class Backup:
    def __init__(self):
        self.working_directory = "/opt/scripts/new_backup/"
        self.mac_address_of_nas = "48:0f:cf:33:e3:aa"
        self.backup_from = "/home/pi/*"
        self.backup_to = "/opt/scripts/new_backup/"
        self.backup_name = "NEW-BACKUP-RPi3.tar.gz"
        self.move_to = "/opt/scripts/new_backup/RemoteBackup/_HOST_BACKUPS/RaspberryPi3/"
        self.ping_counter = 100
        self.parser = ConfigParser()

    def start_nas(self):
        logging.info("Open Media Vault (OMV) is starting...")
        exit_code = subprocess.call("wakeonlan "+ self.mac_address_of_nas, shell=True)
        if exit_code == 0:
            print("OMV has been started!")
        else:
            print("Error {} during starting OMV!".format(exit_code))

    def compress_folders(self):
        print("Executing LOCAL backup process...")
        path_for_backup_file = self.backup_to+self.backup_name
        exit_code = subprocess.call("sudo tar -czf " + path_for_backup_file + " " + self.backup_from, shell=True)
        if exit_code == 0:
            print("Compression is DONE!")
        else:
            print("Compression exited with error {}".format(exit_code))

    def pinger(self, state):
        # Ping once
        # State 1 should be started ONLY ON START of the script to check if OMV is running
        if state == 1:
            print("Check if OMV is already running...")
            exit_code = subprocess.call("ping -c 1 10.0.2.1", shell=True)
            if exit_code == 0:
                print("OMV is running and will not be turned off after backup!!!")
                return False
            else:
                print("OMV is not running and will be turned on!")
                return True

        # Ping until host is not up
        # State 2 should be started after start_nas method to check if OMV booted up
        elif state == 2:
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

    def create_credentials_file(self):
        # Prompt user to insert values inside of credentials.ini
        self.parser['credentials'] = {
            'sysname': input("Please enter system username: "),
            'username': input("Please enter username for network drive: "),
            'password': input("Please enter password for network drive: ")
        }
        # Create credentials.ini and insert values given by user
        with open('./credentials.ini', 'w') as f:
            self.parser.write(f)

        # Changing privileges to root and set read only for root
        subprocess.call("sudo chown root:root credentials.ini", shell=True)
        subprocess.call("sudo chmod 400 credentials.ini", shell=True)

    def credential_operation(self):
        os.chdir(self.working_directory)

        # Check if credentials.ini does exists
        if os.path.exists("credentials.ini"):

            # Check if credentials.ini contains required values
            self.parser.read('credentials.ini')
            if self.parser.get('credentials', 'sysname') == "" \
                    or self.parser.get('credentials', 'username') == "" \
                    or self.parser.get('credentials', 'password') == "":
                print("Configuration file is missing login details...")
                # If there is missing something, start creating credentials.ini again
                self.create_credentials_file()
            else:
                pass
        else:
            print("File does not exist!")
            print("Process of creating new credentials.ini file is in progress...")

            # Creating cred.txt
            self.create_credentials_file()

    def mount_network_drive(self):
        self.parser.read('credentials.ini')

        map_folder = "/opt/scripts/new_backup/RemoteBackup/"
        print("Check if network drive is mounted...")
        if os.path.isdir(self.move_to):
            print("Network drive is ALREADY MOUNTED!")
        else:
            print("Mounting NAS to " + map_folder)
            exit_code = subprocess.call("sudo mount.cifs -v //10.0.2.1/Backup "+map_folder+" -o username="+
                                        self.parser.get('credentials', 'username')+",password="+self.parser.get('credentials', 'password'), shell=True)
            if exit_code == 0:
                print("Network drive has been mounted!")
            else:
                print("\nNAS disk was not succesfully mounted, ERROR CODE {}!!!!!!!!\n".format(exit_code))

    def move_zip_to_nas(self):
        print("Moving compressed file to NAS...")
        exit_code = subprocess.call("sudo mv -f " + self.backup_to+self.backup_name + " " + self.move_to, shell=True)
        if exit_code == 0:
            print("Backup was successfully moved!")
        else:
            print("Error {} occurred!".format(exit_code))

    def shutdown_nas(self):
        print("OMV is shutting down...")
        exit_code = subprocess.call("ssh root@10.0.1.5 'cd /root/;./shutdown.sh'",shell=True)
        if exit_code == 0:
            print("Command to shutdown OMV was successfully executed!")
        else:
            print("Error {} ocurred!".format(exit_code))

    def start(self):
        nas_was_offline = self.pinger(1)
        if nas_was_offline:
            self.start_nas()
        self.compress_folders()
        if nas_was_offline:
            self.pinger(2)
        self.credential_operation()
        self.mount_network_drive()
        self.move_zip_to_nas()
        if nas_was_offline:
            self.shutdown_nas()


backup = Backup()
backup.start()