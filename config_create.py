from configparser import ConfigParser

config = ConfigParser()

config['directories'] = {
    'backup_from': '/home',
    'backup_to': '',
    'backup_name': 'NEW-BACKUP-RPi3.tar.gz',
    'nas_mountpoint': '/media/NASHDD'
}
config['nas_info'] = {
    'nas_ip': '10.0.2.1',
    'nas_mac': '48:0f:cf:33:e3:aa'
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)

