from configparser import ConfigParser

config = ConfigParser(allow_no_value=True)

config['CONFIG'] = {
    '; Logging levels\n; 0 = CRITICAL\n; 1 = ERROR\n; 2 = WARNING\n; 3 = INFO\n; 4 = DEBUG':None,
    'LOG_LEVEL': '0',
    'ping_counter': "100",
    'BACKUP_NAME': '/NEW-BACKUP-RPi3.tar.gz',
    'SRC': '/home'
}

config['NETWORK_DRIVE'] = {
    'IP': '10.0.2.1',
    'MAC': '48:0f:cf:33:e3:aa',
    'BACKUP_TO': '/Backup/_HOST_BACKUPS/raspberrypi/rpi_test',
    'MOUNT_POINT': '/media/NASHDD'
}

with open('config.ini', 'w') as configfile:
    config.write(configfile)

