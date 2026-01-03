#import curses

class Terminal :
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.width, self.height = stdscr.getmaxyx()

    def __clear__(self):
        self.stdscr.clear()

    def reset(self):
        self.stdscr.refresh()

    def printUnit(self, ):
        for

    def printMap(self, player.squad):
        self.stdscr.clear()
        for y in range(self.height):
            for x in range(self.width-1):

    def __placeUnit__(self, unit):

    def __findColor__(self, unit):

    def __findChar__(self, unit):

#verifier si on est dans les limites du terminal


