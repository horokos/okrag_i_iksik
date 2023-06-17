import time
import json
import socket
import struct
import select
from random import randint
from threading import Thread


class Hi_Handler(Thread):
    def __init__(self, function, socket, address):
        Thread.__init__(self, daemon = True)
        self.function = function
        self.socket = socket
        self.address = address

    def run(self):
        self.function(self.socket, self.address)


class Game(Thread):
    def __init__(self, client1, client2, log, queue):
        Thread.__init__(self, daemon = True)
        self.client1 = client1
        self.client2 = client2
        self.queue = queue
        self.log = log
        self.is_end = 0
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.turn = randint(0,1)
        self.start()
    
    def hello_game(self):
        try:
            self.client1.socket.send(self.client1.XorO.encode("UTF-8"))
            self.client2.socket.send(self.client2.XorO.encode("UTF-8"))
        except:
            self.log.error("Couldn't send message terminating game for player: {0} and player: {1}".format(self.player1.name, self.player2.name))
            self.end_game()
    
    def setup_clients(self):
        if self.turn:
            self.client1.XorO = "O"
            self.client2.XorO = "X"
        else:
            self.client1.XorO = "X"
            self.client2.XorO = "O"

    def end_win(self, player):
        player.score += 1
        message = ['win', player.score]
        try:
            message = json.dumps(message)
            player.socket.send(message.encode("UTF-8"))
            self.queue.queue_add(player)
            self.is_end = 1
        except:
            pass
    
    def end_lose(self, player):
        message = ['lose', player.score]
        try:
            message = json.dumps(message)
            player.socket.send(message.encode("UTF-8"))
            self.queue.queue_add(player)
            self.is_end = 1
        except:
            pass

    def send_grid(self, player):
        try:
            message = json.dumps(self.grid)
            player.socket.send(message.encode("UTF-8"))
            return 0
        except:
            self.log.error("Couldn't send message terminating game for player: {0} and player: {1}".format(self.player1.name, self.player2.name))
            self.end_game()
            return 1

    def end_game(self):
        message = ['endgame']
        message = json.dumps(message)
        try:
            message = ['endgame', self.player1.score]
            message = json.dumps(message)
            self.player1.socket.send(message.encode("UTF-8"))

        except:
            pass
        try:
            message = ['endgame', self.player1.score]
            message = json.dumps(message)
            self.player2.socket.send(message.encode("UTF-8"))
        except:
            pass
        self.queue.queue_add(self.player1)
        self.queue.queue_add(self.player2)
        self.is_end = 1
        return 0
    
    def field_used(self, fields):
        """If sb choose existing field skip his tour"""
        if self.grid[fields[0]][fields[1]] == None:
            return 1
        return 0
    
    def field_sanitycheck(self, fields):
        if not isinstance(fields, list):
            return 1
        if (len(fields) != 2):
            return 1
        if int(fields[0]) not in [0, 1, 2]:
            return 1
        if int(fields[1]) not in [0, 1, 2]:
            return 1
        return 0 

    def turns(self):
        self.log.info("Started new game for {0} and {1}".format(self.client1.name, self.client2.name))
        if self.turn:
            self.player1 = self.client1
            self.player2 = self.client2
        else:
            self.player1 = self.client2
            self.player2 = self.client1
        for i in range(9):
            #PLAYER1
            #send grid
            if self.send_grid(self.player1):
                break
            if self.send_grid(self.player2):
                break
            #receive field eg.: [0,1]
            try:
                message = self.player1.socket.recv(2048).decode()
                field = json.loads(message)
                if self.field_sanitycheck(field):
                    raise Exception
            except:
                self.log.error("Couldn't receive or parse message terminating game for player: {0} and player: {1}".format(self.player1.name, self.player2.name))
                self.end_game()
                break
            field = [int(field[0]), int(field[1])]
            if self.field_used(field):
                #update grid
                self.grid[field[0]][field[1]] = self.player1.XorO
                #print(self.grid)
                if self.check_end():
                    break
            #send grid
            if self.send_grid(self.player1):
                break
            if self.send_grid(self.player2):
                break
            #PLAYER2
            #receive field eg.: [0,1]
            try:
                message = self.player2.socket.recv(2048).decode()
                field = json.loads(message)
                if self.field_sanitycheck(field):
                    raise Exception
            except:
                self.log.error("Couldn't receive or parse message terminating game for player: {0} and player: {1}".format(self.player1.name, self.player2.name))
                self.end_game()
                break
            field = [int(field[0]), int(field[1])]
            if self.field_used(field):
                #update grid
                self.grid[field[0]][field[1]] = self.player2.XorO
                #print(self.grid)
                if self.check_end():
                    break
        self.log.debug("End of game for player: {0} score: {2} and player: {1} score: {3}".format(self.player1.name, self.player2.name, self.player1.score, self.player2.score))
        
    def check_end(self):
        """TRZEBA SPRAWDZIC"""
        if None not in sum(self.grid, []):
            self.end_game()
            return 1
        for row in self.grid:
            if set(row) == {'O'}:
                self.end_win(self.player1)
                self.end_lose(self.player2)
                return 1
            elif set(row) == {'X'}:
                self.end_win(self.player2)
                self.end_lose(self.player1)
                return 1
        for c in range(3):
            col = [row[c] for row in self.grid]
            if set(col) == {'O'}:
                self.end_win(self.player1)
                self.end_lose(self.player2)
                return 1
            elif set(col) == {'X'}:
                self.end_win(self.player2)
                self.end_lose(self.player1)
                return 1
        dia1 = []
        dia2 = []
        for d in range(3):
            dia1.append(self.grid[d][d])
            dia2.append(self.grid[2-d][d])
        if set(dia1) == {'O'} or set(dia2) == {'O'}:
            self.end_win(self.player1)
            self.end_lose(self.player2)
            return 1
        elif set(dia1) == {'X'} or set(dia2) == {'X'}:
            self.end_win(self.player2)
            self.end_lose(self.player1)
            return 1
    
    def run(self):
        time.sleep(5)
        self.setup_clients()
        self.hello_game()
        self.turns()


class Queue_Clients(Thread):
    def __init__(self, log):
        Thread.__init__(self, daemon = True)
        self.log = log
        self.queue = []
        self.queue_count = 0
        self.game_list = []
        self.game_count = 0
        self.start()

    def queue_add(self, client):
        self.queue.append(client)
        self.queue_count = len(self.queue)
    
    def del_game(self):
        temp = []
        for g in self.game_list:
            if g.is_end == 0:
                temp.append(g)
        self.game_list = temp
        self.game_count = len(self.game_list)
    
    def pairing(self):
        pairs = self.queue_count // 2
        for i in range(pairs):
            clien1 = self.queue.pop(0)
            clien2 = self.queue.pop(0)
            self.queue_count = len(self.queue)
            game = Game(clien1, clien2, self.log, self)
            self.game_list.append(game)
            self.game_count = len(self.game_list)
    
    def del_client(self, to_delete):
        temp = []
        for i in self.queue:
            if i not in to_delete:
                temp.append(i)
        self.queue = temp
        self.queue_count = len(self.queue)

    def clean(self):
        to_delete = []
        for i in self.queue:
            try:
                rs, _, _ = select.select([i.socket], [], [], 0.01)
                if len(rs) != 0:
                    #print(rs)
                    self.log.debug(rs)
                    i.disconnected()
                    to_delete.append(i)
            except:
                self.log.warning("Non existing connection {0} skipping".format(i.socket))
                to_delete.append(i)
                i.socket.close()
        self.del_client(to_delete)
    
    def queue_show(self):
        self.log.debug(self.queue)

    def queue_funct(self):
        while 1:
            self.clean()
            self.queue_show()
            self.pairing()
            self.del_game()
            time.sleep(1)

    def run(self):
        self.queue_funct()

 
class Ssdp_Client(Thread):
    """Server to listen """
    def __init__(self, current_ip='127.0.0.1', current_port='1900', server_name='kolko-i-krzyzyk'):
        Thread.__init__(self, daemon = True)
        self.current_ip = current_ip
        self.current_port = int(current_port)
        self.server_name = server_name
        self.multicast_group = '239.255.255.250'
        self.multicast_port = 1900
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.multicast_port))
        group = socket.inet_aton(self.multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        self.start()

    def announce_service(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        location='http://{0}:{1}'.format(self.current_ip, str(self.current_port))
        server='kolo-i-krzyzyk'
        message = 'NOTIFY * HTTP/1.1\r\nHOST: {2}:{3}\r\nCACHE-CONTROL: max-age=3600\r\nLOCATION: {0}\r\nSERVER: {1}\r\nNT: unr:kolko-i-krzyzyk:device:server:1\r\nUSN: uuid:09a3c301-00a5-4c89-b9b4-7aec51cad48e::upnp:server\r\nBOOTID.UPNP.ORG:1684012420\r\n\r\n'.format(location,server, self.multicast_group, self.multicast_port)
        message = message.encode("UTF-8")
        sock.sendto(message, (self.multicast_group, self.multicast_port))
        sock.close()

    def discover_services(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            service_info = data.decode('utf-8').split('\r\n\r\n')
            response = service_info[0].split('\r\n')
            if ('M-SEARCH * HTTP/1.1' in response):
                self.announce_service()
    
    def run(self):
        self.discover_services()


class Client(Thread):
    def __init__(self, socket, log):
        Thread.__init__(self, daemon = True)
        self.socket = socket
        self.name = None
        self.XorO = None
        self.score = 0
        self.disconnected = 0
        self.id = randint(1000,9999)
        self.gra = None
        self.log = log
        self.start()
    
    def set_name(self, name):
        self.name = name
    
    def set_fig(self, XorO):
        self.XorO = XorO
    
    def add_score(self, score):
        self.score += int(score)
    
    def clean_score(self):
        self.score = 0
    
    def disconnected(self):
        self.disconnected = 1
    
    def name_sanitycheck(self, name):
        name = name[:15]
        whitelist = "abcdefghijklmnoprstuwxqyzżźćńłśąęó1234567890ABCDEFGHIJKLMNOPRSTUWXYZŻŹĆŃŁĄŚĘÓQ"
        specialchar = '?'
        after_name = ''
        for i in name:
            if i in whitelist:
                after_name += str(i)
            else:
                after_name += str(specialchar)
        self.set_name(name)
    
    
    def server_hello(self):
        try:
            self.log.info("Client starting")
            #odbierz client_hello
            resp = self.socket.recv(2048).decode()
            if resp != "client_hello":
                self.socket.close()
            #wyslij server_hello
            self.socket.send("server_hello".encode("UTF-8"))
            #odbierz username
            resp = self.socket.recv(2048).decode()
            self.name_sanitycheck(resp)
        except OSError as e:
            self.socket.close()

        while 1:
            if self.disconnected:
                break
            time.sleep(0.1)
        self.socket.close()
        return 0
    
    def run(self):
        self.server_hello()