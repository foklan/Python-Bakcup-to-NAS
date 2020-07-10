# Script for backup to NAS
- This script is **only for Linux** systems.
- It chcecks if NAS is running and if not, it will start the NAS with wakeonlan functionality.
- Then it will prompt you to enter **username** and **password** for NAS to mount it under these credentials.
- It will store those credentials to *credentials.ini* file so you don't have to type it again. (only if you want to edit it)
- Then it will create backup from desired source (configure in *config.ini*)
- And finally it will pull *tar.gz* to mounted NAS drive and dismount this drive at the end of the process.

# Installation
1. This script requires package called wakeonlan which can be installed with this command:
- `sudo apt install wakeonlan`

2. Download script by using: 
- `git clone https://github.com/foklan/Python-Bakcup-to-NAS.git`

3. You have to create rsa certificate to allow machine where is backup script running to access NAS without password and shut it down. So this commands should be executed to create certificate and copy it to NAS.
- `ssh-keygen -t rsa`
- `ssh-copy-id -i $HOME/.ssh/id_rsa.pub [user]@[ip of NAS]`
 
4. First time you need to run the script manually for creation of credentials.ini where are the credentials for accessing the NAS. Script will prompt you to enter username and password. So navigate to script destination folder and run following command.
- `sudo python3 backup_script.sh`
