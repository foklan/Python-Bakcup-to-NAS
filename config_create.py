from configparser import ConfigParser as parser

parser['directories'] = {
    'backupFrom': '/home',
    'backupTo': '',
    'backupName': 'NEW-BACKUP-RPi3.tar.gz',
    'nasMountpoint': '/media/NASHDD'
}
parser['nas_info'] = {
    'nasIp': '10.0.2.1',
    'nasMac': '48:0f:cf:33:e3:aa'
}

with open('config.ini', 'w') as f:
    parser.write(f)

