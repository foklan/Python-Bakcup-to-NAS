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
        subprocess.call("wakeonlan"+ self.mac_address_of_nas, shell=True)

    def compress_folders(self):
        print("Executing LOCAL backup process...")
        subprocess.call("sudo tar -cvzf " + self.backup_to+self.backup_name + " *", shell=True)

    def pinger(self):
        pass

    def move_zip_to_nas(self):
        pass

    def start(self):
        self.start_nas()
        self.compress_folders()

backup = Backup()
backup.start()