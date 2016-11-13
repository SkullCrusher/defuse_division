#!/usr/bin/env python3
import logging
import argparse
import curses
import time
import sys

# Since cell probing is donre recursively, for large minefields with fiew
# mines, the default recursion limit may be reached.
sys.setrecursionlimit(5000)


from game.termclient import termclient as tc
from game.server.server import Server
import game

logformat='%(asctime)s:%(levelname)s:%(name)s:%(filename)s:%(lineno)d:%(funcName)s:%(message)s'
logging.basicConfig(format=logformat, filename='client.log', level=logging.DEBUG)

def main():
    # logging.basicConfig(format=logformat, filename='client.log', level=logging.DEBUG)
    logging.debug('Launching minesweeper main')
    parser = argparse.ArgumentParser(
        description="Play a game of minesweeper. Use arrows to move, 'enter' or 'space' to probe, 'f' to flag, CTRL-C to exit."
    )
    parser.add_argument(
        '--height',
        type=int,
        default=16,
        help="the height of the board (default=16)")
    parser.add_argument(
        '--width',
        type=int,
        default=16,
        help="the height of the board (default=16)")
    parser.add_argument(
        '--mines', type=int, default=None, help="number of mines on the board")
    parser.add_argument('--debug', dest='debug', action='store_true')
    parser.add_argument('--vimkeys', dest='vimkeys', action='store_true')
    parser.add_argument('--maxsize', dest='maxsize', action='store_true')
    parser.add_argument('--host', default="127.0.0.1", help='remote host to connect to')
    parser.add_argument('--port', default=44444, type=int, help='port of remote host')
    parser.add_argument('--serveronly', dest='serveronly', action='store_true', help='if true, run as dedicated server')
    parser.set_defaults(space=True)
    parser.set_defaults(debug=False)
    parser.set_defaults(maxsize=False)
    parser.set_defaults(serveronly=False)
    args = parser.parse_args()

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
        srv = Server(args.host, args.port)
        bout = game.game.Bout(max_players=2, player_constructor=srv.create_player)

        try:
            print("Running server on interface '{}' port '{}'".format(args.host, args.port))
            print("Type Ctrl-C to exit")
            while True:
                bout.add_player()
                if len(bout.players) >= bout.max_players:
                    time.sleep(0.3)
        except KeyboardInterrupt:
            return

    # Run our terminal client
    print(curses.wrapper(tc.main, args))

if __name__ == '__main__':
    main()
    # print(curses.wrapper(tc.main))
