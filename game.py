import pygame as pg
import sys
from settings import *
from menu import Menu

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(RES)
        self.clock = pg.time.Clock()
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.turn = 0


    def update(self):
        pg.display.flip()
        self.clock.tick(60)


    def draw(self):
        self.draw_board()
        self.draw_grid()

    def draw_board(self):
        self.screen.fill('pink')
        pg.draw.line(self.screen, 'white', (WIDTH13, 0), (WIDTH13, HEIGHT))
        pg.draw.line(self.screen, 'white', (WIDTH23, 0), (WIDTH23, HEIGHT))
        pg.draw.line(self.screen, 'white', (0, HEIGHT13), (WIDTH, HEIGHT13))
        pg.draw.line(self.screen, 'white', (0, HEIGHT23), (WIDTH, HEIGHT23))

    def draw_grid(self):
        for r, row in enumerate(self.grid):
            for e, element in enumerate(row):
                if element == 'x':
                    pg.draw.line(self.screen, 'white', (WIDTH16 * 0.3 + e * WIDTH13, HEIGHT16 * 0.3 + r * HEIGHT13),
                                 (WIDTH16 + WIDTH16 * 0.7 + e * WIDTH13, HEIGHT16 + HEIGHT16 * 0.7 + r * HEIGHT13),
                                 width=5)
                    pg.draw.line(self.screen, 'white', (WIDTH16 * 0.3 + e * WIDTH13, HEIGHT16 + HEIGHT16 * 0.7 + r * HEIGHT13),
                                 (WIDTH16 + WIDTH16 * 0.7 + e * WIDTH13, HEIGHT16 * 0.3 + r * HEIGHT13),
                                 width=5)
                elif element == 'o':
                    pg.draw.circle(self.screen, 'white', (WIDTH16 + e * WIDTH13, HEIGHT16 + r * HEIGHT13),
                                   WIDTH16 * 0.7, width=5)

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                col = int(pos[0] // WIDTH13)
                row = int(pos[1] // HEIGHT13)
                if self.grid[row][col] == None:
                    if self.turn:
                        self.grid[row][col] = 'x'
                        self.turn = 0
                    else:
                        self.grid[row][col] = 'o'
                        self.turn = 1

    def end(self, gracz):
        self.play = 0
        pg.display.flip()
        print('Wygrywa {0}'.format(gracz))
        pg.time.delay(2000)
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.turn = 0
        pg.event.clear()

    def check_end(self):
        for row in self.grid:
            if set(row) == {'o'}:
                self.end('o')
            elif set(row) == {'x'}:
                self.end('x')
        for c in range(3):
            col = [row[c] for row in self.grid]
            if set(col) == {'o'}:
                self.end('o')
            elif set(col) == {'x'}:
                self.end('x')
        dia1 = []
        dia2 = []
        for d in range(3):
            dia1.append(self.grid[d][d])
            dia2.append(self.grid[2-d][d])
        if set(dia1) == {'o'} or set(dia2) == {'o'}:
            self.end('o')
        elif set(dia1) == {'x'} or set(dia2) == {'x'}:
            self.end('x')

    def run(self):
        while True:
            self.check_events()
            self.update()
            self.draw()
            self.check_end()


game = Game()
game.run()
