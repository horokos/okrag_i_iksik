import socket
import time
import json
import struct
from copy import deepcopy
from threading import Thread


class ServiceAsk(Thread):
    def __init__(self):
        Thread.__init__(self, daemon=True)
        self.multicast_group = '239.255.255.250'
        self.multicast_port = 1900
        self.start()

    def announce_service(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        message = 'M-SEARCH * HTTP/1.1\r\nHOST: {0}:{1}\r\nMAN: ssdp:discover\r\nMX: 5\r\nST: unr:kolko-i-krzyzyk:device:server:1\r\n\r\n'.format(self.multicast_group, self.multicast_port)
        message = message.encode()
        sock.sendto(message, (self.multicast_group, self.multicast_port))
        sock.close()
    
    def run(self):
        for i in range(3):
            self.announce_service()


class ServiceListen(Thread):
    def __init__(self):
        Thread.__init__(self, daemon=True)
        self.multicast_group = '239.255.255.250'
        self.multicast_port = 1900
        self.ip = None
        self.port = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.multicast_port))
        group = socket.inet_aton(self.multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) 
        self.start()

    def discover_services(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            service_info = data.decode('utf-8').split('\r\n\r\n')
            response = service_info[0].split('\r\n')
            print(response)
            if 'NT: unr:kolko-i-krzyzyk:device:server:1' in response:
                for i in response:
                    if 'LOCATION' in i:
                        address = i.replace("LOCATION: http://", "")
                        self.ip, self.port = address.split(":")
                        time.sleep(20) #can be delete only to observe
                        return 1
    
    def run(self):
        self.discover_services()


class Client(Thread):
    def __init__(self, onlineGame, name):
        Thread.__init__(self, daemon=True)
        self.name = name
        self.onlineGame = onlineGame
        self.score = 0
        self.XorO = None
        self.ip = ""
        self.port = 0
        self.start()

    def set_ip_port(self):
        listen = ServiceListen()
        ssdp = ServiceAsk()
        while 1:
            if listen.ip != None and listen.port != None:
                break
            ssdp.announce_service()
            time.sleep(3)
        self.ip = str(listen.ip)
        self.port = int(listen.port)
    
    def message_sanitycheck(self, message):
        message = json.loads(message)
        if isinstance(message, list) and len(message) == 2:
            state = message[1]
            grid = message[0]
        else:
            return ["error"]
        #check grid
        if isinstance(grid, list) and len(grid) == 3:
            try:
                for i in range(3):
                    for j in range(3):
                        if grid[i][j] not in [None, "X", "O"]:
                            return ["error"]
            except:
                return ["error"]
        #check state
        if state not in [ "play", "endgame", "draw", "win", "fail"]:
            return ["error"]
        return [state, grid]
    
    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.client.connect((self.ip, self.port))
        self.client.settimeout(0.1)
        #send client_hello - wait for server to start to listen - serwer queue time to wait equals 1s - because of resources
        time.sleep(1)
        try:
            self.client.send("client_hello".encode("UTF-8"))
            #recv server_hello
            while 1:
                try:
                    mess = self.client.recv(2048).decode("UTF-8")
                    print(mess)
                    if mess != '':
                        break
                except socket.timeout:
                    pass
            self.client.send(self.name.encode("UTF-8"))
            return 1
        except:
            print("Socket error")
            self.client.close()
            return 1
    
    def recv_grid(self):
        try:
            r = 1
            while r:
                if not self.connected:
                    return 2
                try:
                    mess = self.client.recv(2048).decode("UTF-8")
                    print(mess)
                    if mess != '':
                        r = 0
                except socket.timeout:
                    pass
            stategrid = self.message_sanitycheck(mess)
            if stategrid != ["error"]:
                state = stategrid[0]
                grid = stategrid[1]
                #show grid start 
                self.onlineGame.grid = deepcopy(grid)
                self.grid = deepcopy(grid)
                """                print(grid) 
                                for i in range(3):
                                    for j in range(3):
                                        print(grid[i][j], end=" ")
                                    print("")"""

                if state == "play":
                    print(state)
                    return 3
                elif state == "win":
                    print("win!")
                    self.onlineGame.go_endScreen('Wygrywasz!')
                    return 4
                elif state == "fail":
                    print("fail:<")
                    self.onlineGame.go_endScreen('Przegrywasz!')
                    return 4
                elif state == "draw":
                    print(state)
                    self.onlineGame.go_endScreen('Remisujesz!')
                    return 4
                elif state == "endgame":
                    print(state)
                    self.onlineGame.go_endScreen('Przeciwnik stchórzył!')
                    return 1
            else:
                print("error")
                self.client.close()
                return 0
        except:
            print("Error in reciving state and grid")
            return 0
    
    def send_info(self):
        #choosing field
        while self.grid == self.onlineGame.grid:
            if not self.connected:
                return 2
            time.sleep(0.1)
        message = self.onlineGame.last_move
        #choose = input("Podaj 'kolumne wiersz' od 0-2:\n")
        print(message) #[1,1]
        message = json.dumps(message)
        try:
            self.client.send(message.encode("UTF-8"))
            return 0
        except:
            print("Error stop game")
            return 1
    
    def game(self):
        self.XorO = None
        try:
            r = 1
            while r:
                if not self.connected:
                    return 2
                try:
                    mess = self.client.recv(2048).decode()
                    print(mess)
                    if mess != '':
                        r = 0
                except socket.timeout as e:
                    pass
            #recv figure and name
            if mess[0] == "X" or mess[0] == "O":
                self.XorO = mess[0]
                self.oponent = mess[1:]
                self.onlineGame.XorO = self.XorO
                self.onlineGame.opponent_name = mess[1:]
                self.onlineGame.go_play()
            else:
                print("Undefined option ...stopping client")
                return 1
            
            #send OK - synchronize
            self.client.send("OK".encode("UTF-8"))

            #for player with X
            if self.XorO == "X":
                grid = self.recv_grid()
            
            #for player with O
            for round in range(10):
                grid = self.recv_grid()
                if grid in [1, 0]:
                    return 1
                    #end of game
                elif grid == 2:
                    return 2
                elif grid == 4:
                    return 2
                self.onlineGame.turn = 1

                info = self.send_info()
                if info == 2:
                    return 2
                elif info:
                    return 1
                self.onlineGame.turn = 0

                grid = self.recv_grid()
                if grid in [1, 0]:
                    return 1
                    #end of game
                elif grid == 2:
                    return 2
                elif grid == 4:
                    return 2
        except:
            print("Error")
            self.close()
            return 0
        
    def run(self):
        self.set_ip_port() #start socket 
        while True:
            print('nowa gra')
            while not self.onlineGame.connecting:
                pass
                time.sleep(0.05)
            self.connect() #communicate with server
            self.connected = 1
            self.onlineGame.go_queue()
            go_to_queue = self.game()
            if go_to_queue == 1:
                print('koniec gry')
                self.onlineGame.go_endScreen('Opponent left')
                self.close()
            elif go_to_queue == 0:
                return 0

    
    def close(self):
        self.connected = 0
        self.client.shutdown(socket.SHUT_RDWR)

if __name__ == "__main__":
    client = Client("Kot")
    client.main_client()