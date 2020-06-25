from configparser import ConfigParser

config = ConfigParser()

config['FILE'] = {
    'BACKUP_FROM': '/home',
    'BACKUP_TO': '/_HOST_BACKUPS/rpi_test',
    'BACKUP_NAME': '/NEW-BACKUP-RPi3.tar.gz',
    'NAS_MOUNTPOINT': '/media/NASHDD'
}
config['NAS_INFO'] = {
    'IP': '10.0.2.1',
    'MAC': '48:0f:cf:33:e3:aa',
    'BACKUP_FOLDER': '/Backup'
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)

