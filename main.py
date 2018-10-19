#! /usr/bin/python3
import argparse, selectors, sys
from threading import Thread

from Router import Router


def input_parser():
    """Parses execution arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', action = 'store', dest = 'addr', required = True, help = 'Router address')
    # parser.add_argument("addr", metavar="ADDR", type=str, help = 'Router address')

    parser.add_argument('--update-period', action = 'store', dest = 'period', type=int, required = True, help = 'Router update period')
    # parser.add_argument("period", metavar="PERIOD", type=str, help = 'Router update period')

    parser.add_argument('--startup-commands', action='store', dest='init_file', default= None, required= False, help = 'File to initialize topology')
    # parser.add_argument("init_file", metavar="STARTUP", nargs="?", type=str, help = 'File to initialize topology')

    return parser.parse_args()

def handle_commands(cmd, router):
    if(cmd[0] == 'add'): router.add_link(cmd[1], cmd[2])
    elif(cmd[0] == 'del'): router.remove_link(cmd[1])
    elif(cmd[0] == 'trace'): router.trace(cmd[1])
    elif(cmd[0] == 'update'): router.handle_update({'source': cmd[1], 'destination': "127.0.0.1", "distances": { cmd[2]: cmd[3] }})
    else: print('Invalid command')

def main():
    arguments = input_parser()
    router = Router(arguments.addr, arguments.period)
    selector = selectors.DefaultSelector()

    if (arguments.init_file != None):
        with open(arguments.init_file) as fp:
            for line in fp:
                cmd = line.split()
                handle_commands(cmd, router)

    selector.register(sys.stdin, selectors.EVENT_READ, handle_commands)
    selector.register(router.udp, selectors.EVENT_READ, router.handle_messages)

    while(True):
        events = selector.select()
        for key, _ in events:
            callback = key.data
            if (key.fileobj == sys.stdin):
                cmd = input()
                callback(cmd.split(), router)
            elif (key.fileobj == router.udp):
                callback()
        
if __name__ == '__main__':
    main()