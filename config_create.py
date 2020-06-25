from configparser import ConfigParser as parser

parser['directories'] = {
    'backup_from': '/home',
    'backup_to': '',
    'backup_name': 'NEW-BACKUP-RPi3.tar.gz',
    'nas_mountpoint': '/media/NASHDD'
}
parser['nas_info'] = {
    'nas_ip': '10.0.2.1',
    'nas_mac': '48:0f:cf:33:e3:aa'
}

with open('./config.ini', 'w') as f:
    parser.write(f)

