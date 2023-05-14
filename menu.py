import pygame as pg
import sys
from settings import *
from button import Button
from input import Input
from local_game import LocalGame

class Menu:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.sceens = {}
        self.init_sceens()
        self.sceen = self.sceens['menu']
        self.name1 = ''
        self.name2 = ''

    def update(self):
        pg.display.flip()
        self.clock.tick(60)

    def draw(self):
        self.screen.fill('black')
        for button in self.sceen.values():
            button.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.exit()
            for button in self.sceen.values():
                button.check_event(event)

    def init_sceens(self):
        self.sceens['menu'] = {}
        self.sceens['menu']['local_game'] = Button('local game', self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16, self.go_local_game1)
        self.sceens['menu']['online_game'] = Button('online game', self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.go_online_game)
        self.sceens['menu']['exit'] = Button('exit', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.exit)
        self.sceens['local_game1'] = {}
        self.sceens['local_game1']['enter'] = Button('enter player 1 name', self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16, clickable=False)
        self.sceens['local_game1']['input'] = Input(self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.go_local_game2)
        self.sceens['local_game1']['back'] = Button('back', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.go_menu)
        self.sceens['local_game2'] = {}
        self.sceens['local_game2']['enter'] = Button('enter player 2 name', self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16, clickable=False)
        self.sceens['local_game2']['input'] = Input(self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.lunch_local_game)
        self.sceens['local_game2']['back'] = Button('back', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.go_menu)
        self.sceens['online_game'] = {}
        self.sceens['online_game']['enter_name'] = Button('enter name', self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16, clickable=False)
        self.sceens['online_game']['input'] = Input(self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.set_name1)
        self.sceens['online_game']['back'] = Button('back', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.go_menu)

    def go_local_game1(self):
        self.sceen = self.sceens['local_game1']

    def go_local_game2(self, name):
        self.set_name1(name)
        self.sceen = self.sceens['local_game2']

    def go_online_game(self):
        self.sceen = self.sceens['online_game']

    def go_menu(self):
        self.sceen = self.sceens['menu']

    def set_name1(self, name):
        self.name1 = name

    def set_name2(self, name):
        self.name2 = name

    def lunch_local_game(self, name):
        self.set_name2(name)
        game = LocalGame(self.name1, self.name2)
        game.run()
        self.screen = pg.display.set_mode(RES)
        self.go_menu()

    def exit(self):
        pg.quit()
        sys.exit()

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()

game = Menu()
game.run()