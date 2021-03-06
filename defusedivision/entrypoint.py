#!/usr/bin/env python3
import logging
import argparse
import curses
import time
import sys
import os

# Since cell probing is donre recursively, for large minefields with fiew
# mines, the default recursion limit may be reached.
sys.setrecursionlimit(5000)

# Set the delay on the escape key to be 100 milliseconds
os.environ.setdefault('ESCDELAY', '100')

from .termclient import termclient as tc
from .server.server import Server
from . import game
from .termclient.menus import mainmenu
from .termclient import instance_setup

logformat='%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'

def main():
    parser = argparse.ArgumentParser(
        description="Play a game of minesweeper. Use arrows to move, 'enter' or 'space' to probe, 'f' to flag, CTRL-C to exit."
    )
    parser.add_argument(
        '--height',
        type=int,
        default=None,
        help="the height of the board (default=16)")
    parser.add_argument(
        '--width',
        type=int,
        default=None,
        help="the height of the board (default=16)")
    parser.add_argument(
        '--mines', type=int, default=None, help="number of mines on the board")
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--vimkeys', dest='vimkeys', action='store_true')
    parser.add_argument('--maxsize', dest='maxsize', action='store_true')
    parser.add_argument('--playername', default=None, help='Name of your player')
    # Defaults for host and port are set elsewhere, allowing us to determine if
    # the user provided them or not.
    parser.add_argument('--host', help='remote host to connect to')
    parser.add_argument('--port', help='port of remote host')
    parser.add_argument('--serveronly', dest='serveronly', action='store_true', help='if true, run as dedicated server')
    parser.set_defaults(space=True)
    parser.set_defaults(debug=False)
    parser.set_defaults(maxsize=False)
    parser.set_defaults(serveronly=False)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(format=logformat, filename='/tmp/defusedivision.log', level=logging.DEBUG)
    else:
        logging.basicConfig(format=logformat, filename='/tmp/defusedivision.log', level=logging.INFO)
    logging.debug('Launching minesweeper main')


    # Run a dedicated server
    if args.serveronly:
        # Remove the prior logging configuration
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # Add handler to print logs at logging level INFO to stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(logformat))
        logging.root.addHandler(console)
        host = '0.0.0.0'
        port = '44444'
        if args.host:
            host = args.host
        if args.port:
            port = args.port

        srv = Server(host, int(port))
        bout = game.Bout(max_players=3, minefield_size=(args.width, args.height), player_constructor=srv.create_player)

        try:
            print("Running server on interface '{}' port '{}'".format(host, port))
            print("Type Ctrl-C to exit")
            while True:
                bout.add_player()
                if len(bout.players) >= bout.max_players:
                    time.sleep(0.3)
        except KeyboardInterrupt:
            return

    # Run our terminal client
    print(curses.wrapper(dotheui, args))

def dotheui(stdscr, args):
    '''
    Here we springboard into the various bits of user interface.
    '''
    try:
        uiopts = mainmenu.mainmenu(stdscr)
    except KeyboardInterrupt:
        return ""
    client = instance_setup.create_client(stdscr, args, uiopts)
    stdscr.clear()
    return tc.main(stdscr, client, args)


if __name__ == '__main__':
    main()
