#!/usr/bin/python

import subprocess
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
        self.backup_script_folder = None
        self.backup_log = None
        self.do_backup = None
        self.ping_counter = 100
        self.do_shutdown = None

    def error_code_print(self, code):
        print("Error {} ocurred during execution!".format(code))

    def start_nas(self):
        print("Open Media Vault (OMV) is starting...")
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
        # State 1 should be started ONLY ON START of the script to check if OMV is running
        if state == 1:
            print("Check if OMV is already running...")
            exit_code = subprocess.call("ping -c 1 10.0.2.1", shell=True)
            if exit_code == 0:
                print("OMV is running and will not be turned off after backup!!!")
                self.do_shutdown = False
                return True
            else:
                print("OMV is not running and will be turned on!")
                return False

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

    def credential_operation(self):
        os.chdir(self.working_directory)
        file_exist = os.path.exists("cred.txt")
        if file_exist:
            with open('cred.txt') as f:
                if "password=" in f.read():
                    print("File cred.txt is OK")
                else:
                    print("File si probably empty!")
        else:
            print("File does not exist!")
            print("Process of creating new cred.txt file is in progress...")
            sys_usr = input("Please enter system username: ")
            usr = input("Please enter username for network drive: ")
            psw = input("Please enter password for network drive: ")

            # Creating cred.txt
            print("Creating cred.txt")
            exit_code = subprocess.call("sudo touch cred.txt", shell=True)
            if exit_code == 0:
                print("File cred.txt was successfully created!")
            else:
                self.error_code_print(exit_code)

            # Changing privileges
            exit_code = subprocess.call("sudo chown " + sys_usr + ":" + sys_usr + " cred.txt", shell=True)
            if exit_code == 0:
                print("Privileges successfully granted!")
            else:
                self.error_code_print(exit_code)

            # Inserting config lines into cred.txt
            subprocess.call("sudo echo 'username='"+usr+" >> cred.txt", shell=True)
            subprocess.call("sudo echo 'password='" + psw + " >> cred.txt", shell=True)

            # Changing privileges back to root
            subprocess.call("sudo chown root:root cred.txt", shell=True)
            subprocess.call("sudo chmod 400 cred.txt", shell=True)

    def mount_network_drive(self):
        map_folder = "/opt/scripts/new_backup/RemoteBackup/"
        print("Check if network drive is mounted...")
        if os.path.isdir(self.move_to):
            print("Network drive is ALREADY MOUNTED!")
        else:
            print("Mounting NAS to " + map_folder)
            exit_code = subprocess.call("sudo mount.cifs -v //10.0.2.1/Backup " + map_folder + " -o cred=" + self.working_directory + "cred.txt", shell=True)
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
        if self.do_shutdown:
            print("OMV is shutting down...")
            subprocess.call("ssh root@10.0.1.5 'cd /root/;./shutdown.sh'",shell=True)
        else:
            print("OMV will remain ONLINE!")

    def start(self):
        if self.pinger(1):
            self.start_nas()
        self.compress_folders()
        self.pinger(2)
        self.credential_operation()
        self.mount_network_drive()
        self.move_zip_to_nas()



backup = Backup()
backup.start()