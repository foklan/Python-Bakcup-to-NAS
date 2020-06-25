#!/usr/bin/python3

from configparser import ConfigParser
from getpass import getpass
import subprocess
import logging
import time
import os


class Backup:
    def __init__(self):
        self.parser = ConfigParser()
        self.parser.read('config.ini')
        logging.basicConfig(level=logging.DEBUG, filename="backup.log", format="%(asctime)s:%(levelname)s:%(message)s")
        self.working_directory = os.getcwd()
        self.mac_address_of_nas = self.parser.get('NAS_INFO', 'mac')
        self.backup_from = self.parser.get('FILE', 'backup_from')
        self.backup_to = self.parser.get('FILE', 'backup_to')
        self.backup_name = self.parser.get('FILE', 'backup_name')
        self.move_to = self.parser.get('FILE', 'nas_mountpoint')
        self.ping_counter = 100

    def prepare_workspace(self):
        # Check if NASHDD exists
        if os.path.exists("/media/NASHDD"):
            logging.info("Directory NASHDD already exists!")
        else:
            exit_code = subprocess.call("sudo mkdir /media/NASHDD", shell=True)
            if exit_code == 0:
                logging.info("Directory was successfully created!")
            else:
                logging.error("Error during folder creating process!")

    def start_nas(self):
        logging.info("Open Media Vault (OMV) is starting...")
        exit_code = subprocess.call("wakeonlan "+ self.mac_address_of_nas, shell=True)
        if exit_code == 0:
            logging.info("OMV has been started!")
        else:
            logging.error("Error {} during OMV start!".format(exit_code))

    def compress_folders(self):
        logging.info("Executing LOCAL backup process...")
        path_for_backup_file = self.backup_to+self.backup_name
        exit_code = subprocess.call("sudo tar -czf " + path_for_backup_file + " " + self.backup_from, shell=True)
        if exit_code == 0:
            logging.info("Compression is DONE!")
        else:
            logging.error("Compression exited with error {}".format(exit_code))

    def pinger(self, state):
        # Ping once
        # State 1 should be started ONLY ON START of the script to check if OMV is running
        if state == 1:
            logging.info("Check if OMV is already running...")
            exit_code = subprocess.call("ping -c 1 10.0.2.1", shell=True)
            if exit_code == 0:
                logging.info("OMV is running and will not be turned off after backup!!!")
                return False
            else:
                logging.info("OMV is not running and will be turned on!")
                return True

        # Ping until host is not up
        # State 2 should be started after start_nas method to check if OMV booted up
        elif state == 2:
            logging.info("Waiting for OMV to bootup...")
            while self.ping_counter > 0:
                exit_code = subprocess.call("ping -c 1 10.0.2.1", shell=True)
                self.ping_counter -= 1
                if exit_code == 0:
                    logging.info("OMV is ONLINE!")
                    break
                elif exit_code == 1:
                    logging.info("OMV is still not online...")
                    time.sleep(4)
                else:
                    logging.error("Error {} occurred!".format(exit_code))

    def create_credentials_file(self):
        # Prompt user to insert values inside of credentials.ini
        self.parser['credentials'] = {
            'username': input("Please ENTER USERNAME for network drive: "),
            'password': getpass("Please ENTER PASSWORD for network drive: ")
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
            if self.parser.get('credentials', 'username') == "" or self.parser.get('credentials', 'password') == "":
                logging.warning("Configuration file is missing login details...")
                # If there is missing something, start creating credentials.ini again
                self.create_credentials_file()
            else:
                pass
        else:
            logging.warning("File credentials.ini does not exist!")
            logging.info("Process of creating new credentials.ini file is in progress...")

            # Creating cred.txt
            self.create_credentials_file()

    def mount_network_drive(self):
        self.parser.read('credentials.ini')

        map_folder = "/media/NASHDD"
        logging.info("Check if network drive is mounted...")
        if os.path.isdir(self.move_to):
            logging.info("Network drive is ALREADY MOUNTED!")
        else:
            logging.info("Mounting NAS to " + map_folder)
            exit_code = subprocess.call("sudo mount.cifs -v //10.0.2.1/Backup/_HOST_BACKUPS/rpi_test "+map_folder+" -o username="+
                                        self.parser.get('credentials', 'username')+",password="+self.parser.get('credentials', 'password'), shell=True)
            if exit_code == 0:
                logging.info("Network drive has been mounted!")
            elif exit_code == 32:
                logging.critical("NAS disk was not successfully mounted, check if credentials are correct in credentials.ini!")
            else:
                logging.critical("NAS disk was not successfully mounted, ERROR CODE {}!!!!!!!!\n".format(exit_code))

    def move_zip_to_nas(self):
        logging.info("Moving compressed file to NAS...")
        exit_code = subprocess.call("sudo mv -f " + self.backup_to+self.backup_name + " " + self.move_to, shell=True)
        if exit_code == 0:
            logging.info("Backup was successfully moved!\n")
        else:
            logging.error("Error {} occurred!".format(exit_code))

    def shutdown_nas(self):
        logging.info("OMV is shutting down...")
        exit_code = subprocess.call("ssh root@10.0.1.5 'cd /root/;./shutdown.sh'",shell=True)
        if exit_code == 0:
            logging.info("Command to shutdown OMV was successfully executed!\n")
        else:
            logging.error("Error {} ocurred!".format(exit_code))

    def start(self):
        nas_was_offline = self.pinger(1)
        if nas_was_offline:
            self.start_nas()
        self.compress_folders()
        if nas_was_offline:
            self.pinger(2)
        self.prepare_workspace()
        self.credential_operation()
        self.mount_network_drive()
        self.move_zip_to_nas()
        if nas_was_offline:
            self.shutdown_nas()



backup = Backup()
backup.start()
