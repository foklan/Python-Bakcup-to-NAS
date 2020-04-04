import subprocess

class Backup:
    def __init__(self):
        self.backup_from = "/home/"
        self.backup_to = "/opt/scripts/new_backup/"
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
        error_code = subprocess.call("wakeonlan "+ self.mac_address_of_nas, shell=True)
        if error_code == 0:
            print("OMV has been started!")
        else:
            print("Error {} during starting OMV!".format(error_code))

    def compress_folders(self):
        print("Executing LOCAL backup process...")
        error_code = subprocess.call("sudo tar -cvzf " + self.backup_to+self.backup_name + " /home/pi/*", shell=True)
        if error_code == 0:
            print("Compression is DONE!")
        else:
            print("Compression exited with error {}".format(error_code))

    def pinger(self):
        pass

    def move_zip_to_nas(self):
        pass

    def start(self):
        self.start_nas()
        self.compress_folders()

backup = Backup()
backup.start()