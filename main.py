#! /usr/bin/python3

import argparse
from threading import Thread

from Router import Router


def input_parser():
    """Parses execution arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', action = 'store', dest = 'addr', required = True, help = 'Router address')
    # parser.add_argument("addr", metavar="ADDR", type=str, help = 'Router address')

    parser.add_argument('--update-period', action = 'store', dest = 'period', required = True, help = 'Router update period')
    # parser.add_argument("period", metavar="PERIOD", type=str, help = 'Router update period')

    parser.add_argument('--startup-commands', action='store', dest='init_file', default= None, required= False, help = 'File to initialize topology')
    # parser.add_argument("init_file", metavar="STARTUP", nargs="?", type=str, help = 'File to initialize topology')

    return parser.parse_args()

def handle_commands(command, router):
    cmd = command.split()
    if(cmd[0] == 'add'): router.add_link(cmd[1], cmd[2])
    elif(cmd[0] == 'del'): router.remove_link(cmd[1])
    elif(cmd[0] == 'trace'): router.trace(cmd[1])
    else: print('Invalid command')

def main():
    arguments = input_parser()
    router = Router(arguments.addr, arguments.period)

    if (arguments.init_file != None):
        with open(arguments.init_file) as fp:
            for line in fp:
                cmd = line.split()
                handle_commands(cmd, router)

    # router.handle_messages()

    # Trigger thread to receive messages
    # message_thread = Thread(target = router.handle_messages)

    # Create infinite loop to handle keyboard commands
    while(True):
        cmd = input()
        handle_commands(cmd, router)
        router.handle_messages()
        print(router.routing_table)
        

if __name__ == '__main__':
    main()