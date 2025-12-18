import curses

def menu(options, header):
    return curses.wrapper(lambda stdscr: multiple_choice(stdscr, options, header))

def multiple_choice(stdscr, options, header=None):
    """
    Interactive menu system that allows user to navigate and select options.

    Parameters:
        stdscr: curses window object for rendering
        options: list of menu options to display
        header: optional header text to display above menu

    Returns:
        selected option from the menu
    """
    current_row = 0
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while True:
        stdscr.clear()
        if header:
            stdscr.addstr(0, 0, header)
        for idx, row in enumerate(options):
            y = idx + 1 if header else idx
            if idx == current_row:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(y, 0, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(y, 0, row)

        key = stdscr.getch()
        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(options) - 1:
            current_row += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return options[current_row]
        stdscr.refresh()