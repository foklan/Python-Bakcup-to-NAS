#!/usr/bin/python3

from configparser import ConfigParser
from getpass import getpass
import subprocess
import logging
import time
import os


class Backup:
    def __init__(self):
        self.config_parser = ConfigParser()
        self.cred_parser = ConfigParser()
        self.logging_level()

    def logging_level(self):
        # DEBUG: Detailed information, typically of interest only when diagnosing problems.
        # INFO : Confirmation that things are working as expected.
        # WARNING : An indication that something unexpected happened, or indicative of some problem in the near future (e.g. 'disk space low'). The software is still working as expected.
        # ERROR: Due to a more serious problem, the software has not been able to perform some function.
        # CRITICAL: A serious error, indicating that the program itself may be unable to continue running.
        self.config_parser.read('config.ini')
        log_level = int(self.config_parser.get('CONFIG', 'log_level'))

        my_dict = {0: 'CRITICAL', 1: 'ERROR', 2: 'WARNING', 3: 'INFO', 4: 'DEBUG'}

        logging.basicConfig(level=my_dict[log_level], filename="backup.log",format="%(asctime)s:%(levelname)s:%(message)s")

    def prepare_workspace(self):
        logging.debug("Executing prepare_workspace:")
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
        logging.debug("Executing start_nas:")
        mac_address_of_nas = self.config_parser.get('NETWORK_DRIVE', 'mac')

        logging.info("Open Media Vault (OMV) is starting...")
        exit_code = subprocess.call("wakeonlan " + mac_address_of_nas, shell=True)
        if exit_code == 0:
            logging.info("OMV has been started!")
        else:
            logging.error("Error {} during OMV start!".format(exit_code))

    def compress_folders(self):
        logging.debug("Executing compress_folders:")
        logging.info("Executing LOCAL backup process...")
        put_backup_file_to = '/tmp' + self.config_parser.get('CONFIG', 'backup_name')
        logging.debug("Variable put_backup_file_to: "+put_backup_file_to)
        what_to_backup = self.config_parser.get('CONFIG', 'src')
        logging.debug("Variable what_to_backup:"+what_to_backup)

        exit_code = subprocess.call("sudo tar -czf " + put_backup_file_to + " " + what_to_backup, shell=True)
        if exit_code == 0:
            logging.info("Compression is DONE!")
        else:
            logging.error("Compression exited with error {}".format(exit_code))

    def pinger(self, state):
        self.config_parser.read('config.ini')
        ping_counter = int(self.config_parser.get('CONFIG', 'ping_counter'))
        nas_ip = self.config_parser.get('NETWORK_DRIVE', 'ip')

        logging.debug("Executing pinger:")
        # Ping once
        # State 1 should be started ONLY ON START of the script to check if OMV is running
        if state == 1:
            logging.info("Check if OMV is already running...")
            exit_code = subprocess.call("ping -c 1 "+nas_ip, shell=True)
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
            while ping_counter > 0:
                exit_code = subprocess.call("ping -c 1 "+nas_ip, shell=True)
                ping_counter -= 1
                if exit_code == 0:
                    logging.info("OMV is ONLINE!")
                    break
                elif exit_code == 1:
                    logging.info("OMV is still not online...")
                    time.sleep(4)
                else:
                    logging.error("Error {} occurred!".format(exit_code))

    def create_credentials_file(self):
        logging.debug("Executing create_credentials_file:")
        # Prompt user to insert values inside of credentials.ini
        self.cred_parser['credentials'] = {
            'username': input("Please ENTER USERNAME for network drive: "),
            'password': getpass("Please ENTER PASSWORD for network drive: ")
        }
        # Create credentials.ini and insert values given by user
        with open('credentials.ini', 'w') as credsfile:
            self.cred_parser.write(credsfile)

        # Changing privileges to root and set read only for root
        subprocess.call("sudo chown root:root credentials.ini", shell=True)
        subprocess.call("sudo chmod 400 credentials.ini", shell=True)

    def credential_operation(self):
        logging.debug("Executing credential_operation:")
        os.chdir(os.getcwd())

        # Check if credentials.ini does exists
        if os.path.exists("credentials.ini"):
            # Check if credentials.ini contains required values
            self.cred_parser.read('credentials.ini')
            if self.cred_parser.get('credentials', 'username') == "" and self.cred_parser.get('credentials', 'password') == "":
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
        time.sleep(10)
        logging.debug("Executing mount_network_drive:")
        self.config_parser.read('config.ini')

        ip = self.config_parser.get('NETWORK_DRIVE', 'ip')
        backup_path = self.config_parser.get('NETWORK_DRIVE', 'backup_to')
        mount_point = self.config_parser.get('NETWORK_DRIVE', 'mount_point')
        logging.debug("Created variable backup_path = "+backup_path)
        logging.debug("Created variable mount_point = "+mount_point)

        full_path = "//"+ip+backup_path+" "+mount_point
        logging.debug("Created variable full_path = "+full_path)

        self.cred_parser.read('credentials.ini')
        usr = self.cred_parser.get('credentials', 'username')
        pwd = self.cred_parser.get('credentials', 'password')

        try:
            logging.info("Mounting NAS to " + self.config_parser.get('NETWORK_DRIVE', 'backup_to'))
            exit_code = subprocess.call("sudo mount.cifs -v //" + ip + backup_path + " " + mount_point + " -o username=" + usr + ",password=" + pwd, shell=True)
            if exit_code == 0:
                logging.info("Network drive has been mounted!")
            elif exit_code == 32:
                logging.critical("NAS disk was not successfully mounted due to incorrect login credentials, check if credentials are correct in credentials.ini!")
            else:
                logging.critical("NAS disk was not successfully mounted, ERROR CODE {}!!!!!!!!\n".format(exit_code))
        except:
            pass

    def unmount_network_drive(self):
        logging.debug("Executing unmount_network_drive:")
        self.config_parser.read('config.ini')
        exit_code = subprocess.call("sudo umount "+self.config_parser.get('NETWORK_DRIVE', 'mount_point'), shell=True)
        if exit_code == 0:
            logging.info("Network drive was successfully unmounted!\n")
        else:
            logging.error("Network drive was NOT successfully UNMOUNTED!")

    def move_zip_to_nas(self):
        self.config_parser.read('config.ini')
        logging.debug("Executing move_zip_to_nas:")
        logging.info("Moving compressed file to mount-point...")

        src = '/tmp' + self.config_parser.get('CONFIG', 'backup_name')
        logging.debug("Created variable src = "+src)
        dst = self.config_parser.get('NETWORK_DRIVE', 'mount_point')
        logging.debug("Created variable dst = "+dst)

        exit_code = subprocess.call("sudo mv -f " + src + " " + dst, shell=True)
        if exit_code == 0:
            logging.info("Backup was successfully moved!")
        else:
            logging.error("Error {} occurred during file move!".format(exit_code))

    @staticmethod
    def shutdown_nas():
        logging.debug("Executing shutdown_nas:")
        logging.info("OMV is shutting down...")
        exit_code = subprocess.call("ssh root@10.0.1.5 'poweroff'", shell=True)
        if exit_code == 0:
            logging.info("Command to shutdown OMV was successfully executed!\n")
        else:
            logging.error("Error {} ocurred!".format(exit_code))

    def start(self):
        nas_was_offline = self.pinger(1)
        if nas_was_offline:
            self.start_nas()
        self.credential_operation()
        self.compress_folders()
        if nas_was_offline:
            self.pinger(2)
        self.prepare_workspace()
        try:
            self.mount_network_drive()
            self.move_zip_to_nas()
            self.unmount_network_drive()
            if nas_was_offline:
                self.shutdown_nas()
        except:
            pass


backup = Backup()
backup.start()
