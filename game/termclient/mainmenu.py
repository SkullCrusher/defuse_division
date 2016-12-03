'''
Module mainmenu provides a function which draws a main menu to stdscr and
allows a user to select one of several buttons displayed on the screen. The
return value of the mainmenu function is the selection made by the player.
'''

import curses

from . import ui, curses_colors as colors, multiplayer_menu
TITLE_TEXT = """▗▄▄         ▄▄                       .--_    
▐▛▀█       ▐▛▀                      /    `.!,
▐▌ ▐▌ ▟█▙ ▐███ ▐▌ ▐▌▗▟██▖ ▟█▙    ,-┘ └-.  -*-
▐▌ ▐▌▐▙▄▟▌ ▐▌  ▐▌ ▐▌▐▙▄▖▘▐▙▄▟▌  / ▟▖    \ '|`
▐▌ ▐▌▐▛▀▀▘ ▐▌  ▐▌ ▐▌ ▀▀█▖▐▛▀▀▘  │ ▜     |    
▐▙▄█ ▝█▄▄▌ ▐▌  ▐▙▄█▌▐▄▄▟▌▝█▄▄▌  \       /    
▝▀▀   ▝▀▀  ▝▘   ▀▀▝▘ ▀▀▀  ▝▀▀    `-...-'     
▗▄▄    █         █         █                  
▐▛▀█   ▀         ▀         ▀                  
▐▌ ▐▌ ██  ▐▙ ▟▌ ██  ▗▟██▖ ██   ▟█▙ ▐▙██▖      
▐▌ ▐▌  █   █ █   █  ▐▙▄▖▘  █  ▐▛ ▜▌▐▛ ▐▌      
▐▌ ▐▌  █   ▜▄▛   █   ▀▀█▖  █  ▐▌ ▐▌▐▌ ▐▌      
▐▙▄█ ▗▄█▄▖ ▐█▌ ▗▄█▄▖▐▄▄▟▌▗▄█▄▖▝█▄█▘▐▌ ▐▌      
▝▀▀  ▝▀▀▀▘  ▀  ▝▀▀▀▘ ▀▀▀ ▝▀▀▀▘ ▝▀▘ ▝▘ ▝▘      """

OPTIONS = ["Single player", "Multiplayer", "Host and play"]


def createCenterBtn(stdscr, y, contents):
    '''
    Returns a ui.TextBox horizontally centered at the y position with contents
    as the center of the textbox.
    '''
    # Add padding to x calculation because it't added implictly with the addstr
    # offset.
    x, _ = ui.xycenter(stdscr, ' {} '.format(contents))
    rv = ui.TermBox(stdscr, contents, x, y, len(contents) + 2, 1)
    rv.textinpt.addstr(0, 1, contents)
    rv.textinpt.refresh()
    return rv


def mainmenu(stdscr):
    curses.start_color()
    colors.colors_init()
    curses.curs_set(0)

    # Draw the title text at the top of the screen. Assumes single line TITLE_TEXT.
    title_height = len(TITLE_TEXT.split('\n'))
    ttlx, _ = ui.xycenter(stdscr, TITLE_TEXT.split('\n')[0])
    ttly = 1
    for lno, line in enumerate(TITLE_TEXT.split('\n')):
        stdscr.addstr(ttly+lno, ttlx, line)
    stdscr.refresh()

    # Draw the buttons. Assumes single line button text.
    button_height = 4
    ttl_offset = ttly + title_height + 2
    screen_height, _ = stdscr.getmaxyx()
    screen_height = screen_height - ttl_offset
    spacing = ui.interspace(button_height, len(OPTIONS), screen_height)

    buttons = ui.UIList()
    for idx, opt in enumerate(OPTIONS):
        offset = ttl_offset + (spacing * idx) + (button_height * idx)
        btn = createCenterBtn(stdscr, offset, opt)
        buttons.children.append(btn)
    buttons.get_current().select()

    # Wait for user selection
    rv = {'mode':'', 'connection':dict()}
    while True:
        cur = buttons.get_current()
        key = cur.getkey()
        if key == 'KEY_BTAB' or key == 'KEY_UP':
            buttons.select_prior()
        elif key == '\t' or key == 'KEY_DOWN':
            buttons.select_next()
        elif key == '\n':
            rv['mode'] = cur.label
            break
    # TODO cleanup here
    if rv['mode'] == 'Multiplayer':
        stdscr.clear()
        stdscr.touchwin()
        stdscr.refresh()
        rv['connection'] = multiplayer_menu.multiplayer_menu(stdscr)
    return rv
