#!/usr/bin/python
import sys 
import time 
import json 
import socket
import select
import configparser
import threading
from datetime import datetime
from Serwer import *

if __name__ == '__main__':
    log = ServerLogger()
    state, host, port, timeout,max_connections, debug = load_config('/home/balalaika/Dokumenty/okrag_i_iksik/Serwer/config.ini')
    if state == 'ok':
        print("Loaded configuration")
    else:
        print("Failed in loading configuration, terminating")
        exit()
    log.setlog(debug)
    print("Starting SSDP service")
    ssdp = Ssdp_Client(current_ip=host, current_port=port)
    print("Starting server kolko-i-krzyzyk")
    ServerSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM) 
    ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    
    ServerSocket.listen(max_connections)
    print("Server kolko-i-krzyzyk started")
    print("Starting Queue_handler and initializing Client")
    queue = Queue_Clients(log)
    while True:
        client, address = ServerSocket.accept()
        print(address[0] + ":" + str(address[1]) + " connected")
        client = Client(client, log)
        queue.queue_add(client)
        time.sleep(timeout) #to deletion
        queue.queue_show()
    ServerSocket.close() 