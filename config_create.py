from configparser import ConfigParser
config = ConfigParser()

config['BASIC INFO'] = {}
basicinfo = config['BASIC INFO']
basicinfo['Name'] = 'Marian'
basicinfo['Age'] = '22'

config['NETWORK'] = {'IP': '10.0.1.100',
                     'MASK': '8',
                     'GW': '10.0.1.1',
                     'DNS': '10.0.1.1'}

config['address'] = {'street': 'Mak',
                     'St. number': '8',
                     'Postal code': '01001',
                     'City': 'Zilina'}

with open('config1.ini', 'w') as configfile:
    config.write(configfile)

