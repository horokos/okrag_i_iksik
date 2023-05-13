import pygame as pg
import sys
from settings import *
from button import Button

class Menu:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.buttons = {}
        self.init_buttons()

    def update(self):
        pg.display.flip()
        self.clock.tick(60)

    def draw(self):
        self.screen.fill('black')
        for button in self.buttons.values():
            button.draw()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()

    def init_buttons(self):
        self.buttons['local_game'] = Button('local game', self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16)
        self.buttons['online_game'] = Button('online game', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16)

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()



game = Menu()
game.run()