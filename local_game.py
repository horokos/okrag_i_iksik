import pygame as pg
import sys
from settings import *
from button import Button

class LocalGame:
    def __init__(self, name1, name2):
        pg.init()
        self.screen = pg.display.set_mode((RES[0], RES[1]+100))
        self.clock = pg.time.Clock()
        self.running = True
        self.playing = True
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.turn = 0
        self.player1 = {'name': name1, 'score': '0'}
        self.player2 = {'name': name2, 'score': '0'}
        self.score_layout = {}
        self.init_layout()
        self.end_layout = {}

    def init_layout(self):
        self.score_layout['player1'] = Button(self.player1['name'], self.screen, 0, HEIGHT, WIDTH13, 100, clickable=False)
        self.score_layout['score1'] = Button(self.player1['score'], self.screen, WIDTH13, HEIGHT, WIDTH16, 100,
                                              clickable=False)
        self.score_layout['score2'] = Button(self.player2['score'], self.screen, WIDTH12, HEIGHT, WIDTH16, 100,
                                              clickable=False)
        self.score_layout['player2'] = Button(self.player2['name'], self.screen, WIDTH23, HEIGHT, WIDTH13, 100,
                                              clickable=False)

    def init_end_screen(self, winner):
        if winner == 'draw':
            self.end_layout['winner'] = Button('remis', self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16, clickable=False)
        else:
            self.end_layout['winner'] = Button('zwycięża {}'.format(winner), self.screen, WIDTH16, HEIGHT16, WIDTH23, HEIGHT16, clickable=False)
        self.end_layout['rematch'] = Button('rewanż', self.screen, WIDTH16, HEIGHT512, WIDTH23, HEIGHT16, self.rematch)
        self.end_layout['exit'] = Button('powrót', self.screen, WIDTH16, HEIGHT23, WIDTH23, HEIGHT16, self.exit)

    def update(self):
        pg.display.flip()
        self.clock.tick(60)

    def draw(self):
        if self.playing:
            self.draw_board()
            self.draw_grid()
            self.draw_score()
        else:
            self.draw_end_screen()

    def draw_end_screen(self):
        self.screen.fill('pink')
        for button in self.end_layout.values():
            button.draw()

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

    def draw_score(self):
        if self.turn:
            self.score_layout['player2'].bg_color = 'darkgrey'
            self.score_layout['player1'].bg_color = 'white'
        else:
            self.score_layout['player1'].bg_color = 'darkgrey'
            self.score_layout['player2'].bg_color = 'white'
        for button in self.score_layout.values():
            button.draw()

    def check_events(self):
        for event in pg.event.get():
            print(event)
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if self.playing:
                if event.type == pg.MOUSEBUTTONUP:
                    pos = pg.mouse.get_pos()
                    col = int(pos[0] // WIDTH13)
                    row = int(pos[1] // HEIGHT13)
                    if col < 3 and row < 3:
                        if self.grid[row][col] == None:
                            if self.turn:
                                self.grid[row][col] = 'x'
                                self.turn = 0
                            else:
                                self.grid[row][col] = 'o'
                                self.turn = 1
            else:
                for button in self.end_layout.values():
                    button.check_event(event)

    def end(self, gracz):
        if gracz['name'] != 'draw':
            gracz['score'] = str(int(gracz['score']) + 1)
            if gracz is self.player1:
                self.score_layout['score1'].text = self.score_layout['score1'].font.render(gracz['score'], True, 'black')
            else:
                self.score_layout['score2'].text = self.score_layout['score1'].font.render(gracz['score'], True, 'black')
        pg.display.flip()
        pg.time.delay(500)
        self.grid = [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ]
        self.playing = False
        self.init_end_screen(gracz['name'])
        self.turn = 0
        pg.event.clear()

    def check_end(self):
        if None not in sum(self.grid, []):
            self.end({'name': 'draw'})
        for row in self.grid:
            if set(row) == {'o'}:
                self.end(self.player1)
            elif set(row) == {'x'}:
                self.end(self.player2)
        for c in range(3):
            col = [row[c] for row in self.grid]
            if set(col) == {'o'}:
                self.end(self.player1)
            elif set(col) == {'x'}:
                self.end(self.player2)
        dia1 = []
        dia2 = []
        for d in range(3):
            dia1.append(self.grid[d][d])
            dia2.append(self.grid[2-d][d])
        if set(dia1) == {'o'} or set(dia2) == {'o'}:
            self.end(self.player1)
        elif set(dia1) == {'x'} or set(dia2) == {'x'}:
            self.end(self.player2)

    def rematch(self):
        self.playing = True

    def exit(self):
        self.running = False

    def run(self):
        while self.running:
            self.check_events()
            self.update()
            self.draw()
            self.check_end()


# game = Game()
# game.run()
