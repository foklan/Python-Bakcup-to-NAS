from configparser import ConfigParser

config = ConfigParser()

config['FILE'] = {
    'BACKUP_NAME': '/NEW-BACKUP-RPi3.tar.gz'
}
config['NETWORK_DRIVE'] = {
    'IP': '10.0.2.1',
    'MAC': '48:0f:cf:33:e3:aa',
    'BACKUP_TO': '/Backup/_HOST_BACKUPS/rpi_test',
    'MOUNT_POINT': '/media/NASHDD'
}

config['COMPRESS'] = {
    'SRC': '/home',
    'DST': '/tmp'
}

config['MOVER'] = {
    'SRC': "tmp",
    'DST': "/media/NASHDD/"
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)

