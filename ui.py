import curses
import sys
from copy import deepcopy
# from .utils import menu #IDK if I'll use this

class Board:
    def __init__(self, name):
        self.name = name
        self.board = [[0 for i in range(10)] for i in range(10)]

class PlaceBoat:
    def __init__(self, ship: int, obj):
        self.ship = [ship for i in range(ship)]
        self.obj = obj
        self.board = deepcopy(obj.board)
        self.working_board = deepcopy(self.board)
        x = 4
        y = 4
        self.coor = {y+i: x for i in range(ship)}
        self.reference_coor = (y,x)
        self.angle = 90


    def update_ship(self):
        ship = self.ship[0]
        y,x = self.reference_coor # Point of rotation
        
        if self.angle == 90:
            self.coor = {y+i: x for i in range(ship)}
        elif self.angle == 180:
            self.coor = {y: [x-i for i in range(ship)]}
        elif self.angle == 270:
            self.coor = {y - i: x for i in range(ship)}
        else:
            self.coor = {y: [x+i for i in range(ship)]}
        
    def reset_position(self):
        self.coor = {4+i: 4 for i in range(self.ship[0])}

    def concatenate_coor(self):
        return list(map(list, self.coor.items()))

    def flatten_coor(self):
        flat_list = []
        for k, v in self.coor.items():
            flat_list.extend([k, v])
        return flat_list

    def valid_position(self):
        array = self.flatten_coor()
        if max(array) > 9:
            self.legal = False
        elif min(array) < 0: 
            self.legal = False
        else: self.legal = True
    
    def place_ship(self):
        for key, val in self.coor.items():
            self.obj.board[key][val] = self.ship[0]

    def check_offscreen(self):
        Xs, Ys = list(self.coor.values()), list(self.coor.keys())
        if min(Xs) > 9: 
            self.reset_position()
        if max(Xs) < 0:
            self.reset_position()
        if max(Ys) > 9:
            self.reset_position()
        if min(Ys) < 0:
            self.reset_position()

    def update_board(self):
        self.working_board = deepcopy(self.board)
        for y,x in self.coor.items():
            self.working_board[y][x] = self.ship[0]
    
    def concatenate_coor(self):
        coor = self.coor
        output = []
        for key in coor:
            if type(key) == int:
                output.append([key, coor[key]])
                continue
            for val in key:
                output.append([key,val])

        return output
                

    def get_position(self):
        """
        Gets coordinate selection from user using arrow keys.

        Returns:
            tuple of (row, column) coordinates
        """
        header = 'Place the boat:\n\n'
        return curses.wrapper(lambda stdscr: self.position_boat(stdscr, header))

    def position_boat(self, stdscr, header):
        """
        Interactive coordinate selection with arrow key navigation.

        Parameters:
            stdscr: curses window
            header: display header

        Returns:
            tuple of (x, y) board coordinates
        """
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        
        RED_ON_BLACK = curses.color_pair(2)
        GREEN_ON_BLACK = curses.color_pair(3)
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)  # Enable special keys

        while True:
            stdscr.clear()
            if header:
                stdscr.addstr(0, 0, header)
            self.valid_position()
            self.check_offscreen()
            self.update_board()

            # Highlight Green or Red for the ship depending on validity of placement
            # Don't highlight otherwise
            Ccoor = self.concatenate_coor()
            for y, sublist in enumerate(self.working_board): # TODO: FIX ISSUE WITH THE ARRAY VALS BEING AN ARRAY OR INT
                for x, item in enumerate(sublist):
                    if [y, x] in [[y2, x2] for y2, x2 in self.coor.items()]:
                        if self.legal:
                            stdscr.addstr(y + 1, x * 4, str(item), GREEN_ON_BLACK)
                        else:
                            stdscr.addstr(y + 1, x * 4, str(item), RED_ON_BLACK)
                    else:
                        stdscr.addstr(y + 1, x * 4, str(item))

            key = stdscr.getch()
            y, x = self.reference_coor
            if key == curses.KEY_UP:
                y = max(0, y - 1)
            elif key == curses.KEY_DOWN:
                y = min(len(self.board) - 1, y + 1)
            elif key == curses.KEY_LEFT:
                x = max(0, x - 1)
            elif key == curses.KEY_RIGHT:
                x = min(len(self.board[y]) - 1, x + 1)
            elif key == ord('r'):
                self.angle += 90
                if self.angle > 360:
                    self.angle -= 360
            elif key == ord('\n'):
                self.place_ship()
                return

            self.reference_coor = (y,x)
            self.update_ship()
            self.update_board()

    
if __name__ == "__main__":
    game = Board('Simon - P1')
    PlaceBoat(4, game).get_position()