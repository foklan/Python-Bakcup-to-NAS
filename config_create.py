from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)

config['CONFIG'] = {
    '; Logging levels\n; 0 = CRITICAL\n; 1 = ERROR\n; 2 = WARNING\n; 3 = INFO\n; 4 = DEBUG':None,
    'LOG_LEVEL': '0'
}

config['FILE'] = {
    'BACKUP_NAME': '/NEW-BACKUP-RPi3.tar.gz'
}
config['NETWORK_DRIVE'] = {
    'IP': '10.0.2.1',
    'MAC': '48:0f:cf:33:e3:aa',
    'BACKUP_TO': '/Backup/_HOST_BACKUPS/raspberryppi/rpi_test',
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

config['PINGER'] = {
    'ping_counter': "100"
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)

