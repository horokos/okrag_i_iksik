import socket
import time
import json
import struct
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


class Client():
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.XorO = None
        self.ip = ""
        self.port = 0
    
    def multiple_message_clean_go_queue(self, strr):
        strr = str(strr)
        if '["endgame", 1]' in strr and ('X' in strr or 'O' in strr):
            self.client.send("UPS")
            self.client.recv(2048).decode("UTF-8")
            return 2


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
    
    def message_type(self, message):
        message = json.loads(message)
        if isinstance(message, list) and len(message) == 3:
            try:
                for i in range(3):
                    for j in range(3):
                        if message[i][j] in [None, "X", "O"]:
                            print("mt - grid")
                            return "grid"
            except:
                return "error"
        if isinstance(message, list) and len(message) == 2:
            if message[0] == "win" or message[0] == "endgame" or message[0] == "lose":
                return "end"
            else:
                return "error"
        return "error"
    
    def connect(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM,)
        self.client.connect((self.ip, self.port))
        #send client_hello - wait for server to start to listen - serwer queue time to wait equals 1s - because of resources
        time.sleep(1)
        try:
            self.client.send("client_hello".encode("UTF-8"))
            #recv server_hello
            while 1:
                mess = self.client.recv(2048).decode("UTF-8")
                print(mess)
                if mess != '':
                    break
            self.client.send(self.name.encode("UTF-8"))
            return 1
        except:
            print("Socket error")
            self.client.close()
            return 1
    
    def recv_grid(self):
        try:
            while 1:
                mess = self.client.recv(2048).decode("UTF-8")
                print(mess)
                if mess != '':
                    break
            if self.message_type(mess) == "grid":
                grid = json.loads(mess)
                #show grid start --- can be deleted - HIERONIM
                print(grid) #[[None, None, None], [None, None, None], [None, "X", "O"]]
                for i in range(3):
                    for j in range(3):
                        print(grid[i][j], end=" ")
                    print("")
                #show grid stop --- can be deleted - merge with GUI
                return 0
            elif self.message_type(mess) == "end":
                message = json.loads(mess)
                if message[0] == "win":
                    self.score = message[1]
                    print(self.score) #HIERONIM
                    print("win!")#HIERONIM
                    return 2
                if message[0] == "lose":
                    self.score = message[1]
                    print(self.score)#HIERONIM
                    print("lose:<")#HIERONIM
                    return 2
                if message[0] == "endgame":
                    self.score = message[1]
                    print(self.score)#HIERONIM
                    print("endofgame")#HIERONIM
                    return 2
            elif self.message_type(mess) == "error":
                print("error")
                self.client.close()
                return 1
        except:
            print("Error in reciving grid")
            return 1
    
    def send_info(self):
        #choosing field
        choose = input("Podaj 'kolumne wiersz' od 0-2:\n")#HIERONIM
        message = choose.split(" ")#HIERONIM można usunąć niech w messages zostanie lista[współrzędna_x, współrzędna_y]
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
            while 1:
                mess = self.client.recv(2048).decode()
                print(mess)
                if mess != '':
                    break
            if mess == "X" or mess == "O":
                self.XorO = mess
            else:
                print("Undefined option ...stopping client")
            #for player with X
            if self.XorO == "X":
                self.recv_grid()
            for round in range(10): #not 9 because sb can win in 10th round
                grid = self.recv_grid()
                if grid == 1:
                    return 1
                elif grid == 2:
                    return 2
                    #end of game go to queue
                info = self.send_info()
                if info:
                    return 1
                
                grid = self.recv_grid()
                if grid == 1:
                    return 1
                elif grid == 2:
                    return 2
                    breakimage.png
                    #end of game go to queue
        except:
            print("Error")
            self.client.socket()
        
    def main_client(self):
        self.set_ip_port() #start socket 
        self.connect() #communicate with server
        while 1:
            go_to_queue = self.game()
            if go_to_queue == 1:
                self.client.close()
                break
            elif go_to_queue == 2:
                continue


if __name__ == "__main__":
    client = Client("Kot") #tutaj podaje sie name
    client.main_client()