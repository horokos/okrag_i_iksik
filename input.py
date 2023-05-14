import pygame as pg

class Input:
    def __init__(self, screen, x, y, width, height, target):
        pg.init()
        self.screen = screen
        self.target = target
        self.text = ''
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = pg.font.SysFont('Arial', 40)
        self.text_surface = self.font.render(self.text, True, 'black')
        self.surface = pg.Surface((self.width, self.height))
        self.bg_color = 'white'
        self.text_rect = self.text_surface.get_rect(center=(self.width/2, self.height/2))
        self.input_rect = pg.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        self.surface.fill(self.bg_color)
        self.surface.blit(self.text_surface, self.text_rect)
        self.screen.blit(self.surface, self.input_rect)

    def check_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pg.K_RETURN:
                self.target(self.text)
            elif len(self.text)<11:
                self.text += event.unicode
            self.text_surface = self.font.render(self.text, True, 'black')
            self.text_rect = self.text_surface.get_rect(center=(self.width / 2, self.height / 2))
            self.input_rect = pg.Rect(self.x, self.y, self.width, self.height)