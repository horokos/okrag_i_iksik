import pygame as pg
from settings import *

class Button:
    def __init__(self, text, screen, x, y, width, height):
        pg.init()
        self.screen = screen
        self.font = pg.font.SysFont('Arial', 40)
        self.text = self.font.render(text, True, 'black')
        self.surface = pg.Surface((width, height))
        self.surface.fill('white')
        self.text_rect = self.text.get_rect(center=(width/2, height/2))
        self.button_rect = pg.Rect(x, y, width, height)

    def draw(self):
        self.surface.blit(self.text, self.text_rect)
        self.screen.blit(self.surface, self.button_rect)
