import pygame as pg

class Button:
    def __init__(self, text, screen, x, y, width, height, target=None, clickable=True):
        pg.init()
        self.clickable = clickable
        self.target = target
        self.screen = screen
        self.font = pg.font.SysFont('Arial', 40)
        self.text = self.font.render(text, True, 'black')
        self.surface = pg.Surface((width, height))
        self.bg_color = 'white'
        self.text_rect = self.text.get_rect(center=(width/2, height/2))
        self.button_rect = pg.Rect(x, y, width, height)

    def draw(self):
        self.surface.fill(self.bg_color)
        self.surface.blit(self.text, self.text_rect)
        self.screen.blit(self.surface, self.button_rect)

    def check_event(self, event):
        if self.clickable:
            if event.type == pg.MOUSEMOTION:
                pos = pg.mouse.get_pos()
                self.bg_color = 'white'
                if self.button_rect.collidepoint(pos):
                    self.bg_color = 'grey'
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                if self.button_rect.collidepoint(pos):
                    self.target()
