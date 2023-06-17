import configparser
from time import sleep


def load_config(config_path='./Serwer/config.ini'):
    """Load server variables from config.ini"""
    config = configparser.ConfigParser()
    config.read(config_path)
    state = 'error'
    try:
        prod_dev = str(config['Server']['PROD_DEV'])
        if prod_dev == 'dev':
            host = str(config['Server']['LOCAL_HOST_IP'])
            port = int(config['Server']['LOCAL_HOST_PORT'])
        else:
            port = int(config['Server']['HOST_PORT'])
            host = str(config['Server']['HOST_IP'])
        timeout = float(config['Server']['TIMEOUT'])
        max_connections = int(config['Server']['MAX_CONNECTIONS'])
        debug = int(config['Server']['DEBUG'])
        state = 'ok'
    except:
        prod_dev = 0
        host = 0
        port = 0
        timeout = 0
        max_connections = 0
    return state, host, port, timeout, max_connections, debug