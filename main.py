import argparse

from Router import Router


def input_parser():
    """Parses execution arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument('--addr', action = 'store', dest = 'addr', required = True, help = 'Router address')
    parser.add_argument('--update-period', action = 'store', dest = 'period', required = True, help = 'Router update period')
    parser.add_argument('--startup-commands', action='store', dest='init_file', default= None, required= False, help = 'File to initialize topology')

    return parser.parse_args()

def main():
    arguments = input_parser()
    router = Router(arguments.addr, arguments.period)

    if (arguments.init_file != None):
        with open(arguments.init_file) as fp:
            for line in fp:
                # Handle topology through file 
                print(line)


    print(vars(router))

    while(True):
        

if __name__ == '__main__':
    main()