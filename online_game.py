import pygame as pg
import sys
from settings import *
from button import Button
from threading import Thread
from client import Client

class OnlineGame:
    def __init__(self, name):
        pg.init()
        self.screen = pg.display.set_mode((RES[0], RES[1]+100))
        self.clock = pg.time.Clock()
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.running = True
        self.name = name
        self.opponent_name = None
        self.turn = 0
        self.search = 1
        self.connecting = 0
        self.in_queue = 0
        self.playing = 0
        self.breakScreen = 0
        self.client = Client(self, self.name)
        self.sceens = {}
        self.init_search_layout()
        self.init_connecting_layout()
        self.init_queue_layout()
        self.init_breakScreen_layout()
        self.sceen = self.sceens['search_layout']
        self.last_move = None
        self.turn = 0
        self.XorO = None
        

    def init_connecting_layout(self):
        self.sceens['connecting_layout'] = {}
        self.sceens['connecting_layout']['connecting'] = Button('łączenie', self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, clickable=False)

    def init_queue_layout(self):
        self.sceens['queue_layout'] = {}
        self.sceens['queue_layout']['queue'] = Button('w kolejce', self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, clickable=False)
        self.sceens['queue_layout']['exit'] = Button('opuść kolejkę', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.exit_game)
        
    def init_search_after_game_layout(self, message):
        self.sceens['search_layout'] = {}
        self.sceens['search_layout']['search'] = Button('szukaj gry', self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.go_connecting)
        self.sceens['search_layout']['message'] = Button(message, self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16, clickable=False)
        self.sceens['search_layout']['exit'] = Button('wyjdź', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.exit)
        
    def init_search_layout(self):
        self.sceens['search_layout'] = {}
        self.sceens['search_layout']['search'] = Button('szukaj gry', self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.go_connecting)
        self.sceens['search_layout']['exit'] = Button('wyjdź', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.exit)
        
    def init_breakScreen_layout(self):
        self.sceens['breakScreen_layout'] = {}
        self.sceens['breakScreen_layout']['exit'] = Button('wyjdź z gry', self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.exit_game)
        
    def init_players_layout(self):
        self.sceens['players_layout'] = {}
        self.sceens['players_layout']['player1'] = Button(self.name, self.screen, 0, HEIGHT, WIDTH12, 100, clickable=False)
        self.sceens['players_layout']['player2'] = Button(self.opponent_name, self.screen, WIDTH12, HEIGHT, WIDTH12, 100, )


    def update(self):
        pg.display.flip()
        self.clock.tick(60)
        #print('self.turn = {0} self.connected = {1} self.in_queue = {2} self.playing = {3}'.format(self.turn, self.connected, self.in_queue, self.playing))

    def draw(self):
        if self.search:
            self.draw_search()
        elif self.connecting:
            self.draw_connecting()
        elif self.in_queue:
            self.draw_queue()
        elif self.breakScreen:
            self.draw_breakScreen()
        elif self.playing:
            self.draw_board()
            self.draw_grid()
            self.draw_players()

    def draw_search(self):
        self.screen.fill('pink')
        for button in self.sceens['search_layout'].values():
            button.draw()

    def draw_connecting(self):
        self.screen.fill('pink')
        for button in self.sceens['connecting_layout'].values():
            button.draw()

    def draw_queue(self):
        self.screen.fill('pink')
        for button in self.sceens['queue_layout'].values():
            button.draw()
            
    def draw_breakScreen(self):
        self.screen.fill('pink')
        for button in self.sceens['breakScreen_layout'].values():
            button.draw()

    def draw_board(self):
        self.screen.fill('pink')
        pg.draw.line(self.screen, 'white', (WIDTH13, 0), (WIDTH13, HEIGHT))
        pg.draw.line(self.screen, 'white', (WIDTH23, 0), (WIDTH23, HEIGHT))
        pg.draw.line(self.screen, 'white', (0, HEIGHT13), (WIDTH, HEIGHT13))
        pg.draw.line(self.screen, 'white', (0, HEIGHT23), (WIDTH, HEIGHT23))
        pg.draw.line(self.screen, 'white', (0, HEIGHT), (WIDTH, HEIGHT))

    def draw_grid(self):
        for r, row in enumerate(self.grid):
            for e, element in enumerate(row):
                if element == 'X':
                    pg.draw.line(self.screen, 'white', (WIDTH16 * 0.3 + e * WIDTH13, HEIGHT16 * 0.3 + r * HEIGHT13),
                                 (WIDTH16 + WIDTH16 * 0.7 + e * WIDTH13, HEIGHT16 + HEIGHT16 * 0.7 + r * HEIGHT13),
                                 width=5)
                    pg.draw.line(self.screen, 'white', (WIDTH16 * 0.3 + e * WIDTH13, HEIGHT16 + HEIGHT16 * 0.7 + r * HEIGHT13),
                                 (WIDTH16 + WIDTH16 * 0.7 + e * WIDTH13, HEIGHT16 * 0.3 + r * HEIGHT13),
                                 width=5)
                elif element == 'O':
                    pg.draw.circle(self.screen, 'white', (WIDTH16 + e * WIDTH13, HEIGHT16 + r * HEIGHT13),
                                   WIDTH16 * 0.7, width=5)
                                   
    def draw_players(self):
        if not self.turn:
            self.sceens['players_layout']['player2'].bg_color = 'salmon'
            self.sceens['players_layout']['player1'].bg_color = 'white'
        else:
            self.sceens['players_layout']['player1'].bg_color = 'salmon'
            self.sceens['players_layout']['player2'].bg_color = 'white'
        for button in self.sceens['players_layout'].values():
            button.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE and self.playing:
                    self.breakScreen = not self.breakScreen
            if self.playing and self.turn and not self.breakScreen:
                if event.type == pg.MOUSEBUTTONUP:
                    pos = pg.mouse.get_pos()
                    col = int(pos[0] // WIDTH13)
                    row = int(pos[1] // HEIGHT13)
                    if self.grid[row][col] == None:
                            self.grid[row][col] = self.XorO
                    self.last_move = [row, col]
                    print(self.grid)
            elif not self.playing or self.breakScreen:
                for button in self.sceen.values():
                    button.check_event(event)

    def go_search(self):
        self.search = 1
        self.in_queue = 0
        self.connecting = 0
        self.playing = 0
        self.breakScreen = 0
        self.init_search_layout()
        self.sceen = self.sceens['search_layout']

    def go_connecting(self):
        self.search = 0
        self.in_queue = 0
        self.connecting = 1
        self.playing = 0
        self.breakScreen = 0
        self.sceen = self.sceens['connecting_layout']

    def go_queue(self):
        self.search = 0
        self.in_queue = 1
        self.connecting = 0
        self.playing = 0
        self.breakScreen = 0
        self.sceen = self.sceens['queue_layout']
        
    def exit_game(self):
        print('exiting game')
        self.client.close()
        self.go_search()

        
    def go_play(self):
        self.init_players_layout()
        self.search = 0
        self.in_queue = 0
        self.connected = 0
        self.playing = 1
        self.breakScreen = 0
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.sceen = self.sceens['breakScreen_layout']
        
        
    def go_endScreen(self, message):
        self.init_search_after_game_layout(message)
        self.search = 1
        self.in_queue = 0
        self.connected = 0
        self.playing = 0
        self.breakScreen = 0
        self.sceen = self.sceens['search_layout']
        
    def exit(self):
        self.running = False

    def run(self):
        while self.running:
            self.check_events()
            self.update()
            self.draw()
