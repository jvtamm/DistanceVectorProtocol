# Every router needs to be an instance of Router with its own UDP socket
# 	Cada roteador será associado (bind)
# Command add <ip> <weight> creates a link between the running router and <ip> router with a <weight>
# Command del <ip> removes a link between the running router and <ip>

# https://owncloud.dcc.ufmg.br/index.php/s/3ZF96YV9JVY06CF#pdfviewer
# http://www.mathcs.emory.edu/~cheung/Courses/558/Syllabus/13-Routing/distance-vec1.html
# https://codereview.stackexchange.com/questions/83790/pydos-shell-simulation
# https://github.com/gu9/testpython-/blob/master/pg01_gu9.py
import socket, struct

class Router:
    def __init__(self, addr, period):
        self.table = dict() # Key -> destination addr | Value -> Tuple (weight, nextHop)
        self.period = period    # Might be deleted when timer is created

        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((addr, 55151))