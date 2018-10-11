# Every router needs to be an instance of Router with its own UDP socket
# 	Cada roteador será associado (bind)
# Command add <ip> <weight> creates a link between the running router and <ip> router with a <weight>
# Command del <ip> removes a link between the running router and <ip>

# https://owncloud.dcc.ufmg.br/index.php/s/3ZF96YV9JVY06CF#pdfviewer
# http://www.mathcs.emory.edu/~cheung/Courses/558/Syllabus/13-Routing/distance-vec1.html
# https://codereview.stackexchange.com/questions/83790/pydos-shell-simulation
# https://github.com/gu9/testpython-/blob/master/pg01_gu9.py
import socket, sys, json
from collections import defaultdict as dd
from threading import Lock

class Router:
    def __init__(self, addr, period):
        self.routing_table = dd(lambda: dd(list)) # Key -> destination addr | Value -> [Tuple (distance, nextHop)]
        self.link_table = dict()    # Key -> destination | Value -> Weight
        self.period = period    # Might be deleted when timer is created

        self.link_lock = Lock()
        self.routing_lock = Lock()

        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((addr, 55151))

    
    # Command handlers

    def add_link(self, addr, weight):
        if (addr == self.udp.getsockname()[0]): sys.exit("Tried to add a link to itself")

        self.link_lock.acquire()
        self.link_table[addr] = int(weight)
        self.link_lock.release()

    def remove_link(self, addr):
        self.revome_routing_table_via(addr)

        self.link_lock.acquire()
        del self.link_table[addr]
        self.link_lock.acquire()
        

    def trace(self, ip):
        print(self)
        print('Should implement trace function')


    # Message type handlers

    def handle_messages(self):
        actions = {'data': self.handle_data, 'update': self.handle_update, 'trace': self.handle_trace}
        # data = json.dumps({"source": "127.0.0.4", "destination": "127.0.0.2", "type": "data", "payload": "{\"source\": \"127.0.0.2\", \"destination\": \"127.0.0.4\", \"type\": \"trace\", \"hops\": [\"127.0.0.1\", \"127.0.0.4\"]}"})
        data = json.dumps({ "type": "update","source": "127.0.1.5","destination": "127.0.0.1","distances": {"127.0.1.4": 10,"127.0.1.5": 0,"127.0.1.2": 10,"127.0.1.3": 10}})
        formated_data = json.loads(data)

        print(data)

        if(formated_data['type'] in actions):
            action = actions[formated_data['type']]
            action(formated_data)
    
    def handle_data(self, data):
        if (data['destination'] == self.udp.getsockname()[0]): 
            print(data['payload'])
        else:
            print('Should check routing table, get shortest route, and send to nextHop')
            self.routing_lock.acquire()

            self.routing_lock.release()

    def handle_update(self, data):
        if (data['destination'] != self.udp.getsockname()[0]):
            print('Destination is not this router')
            return

        self.link_lock.acquire()
        
        
        if (not data['source'] in self.link_table):
            print('Update message being sent through a non existing link')
            self.link_lock.release()
            return
        
        self.revome_routing_table_via(data['source'])

        self.routing_lock.acquire()

        for key, value in data['distances'].items():
            distance = int(value) + self.link_table[data['source']]
            print(distance)
            self.routing_table[key][data['source']].append(distance)
            print(self.routing_table[key][data['source']])

        self.link_lock.release()
        self.routing_lock.release()

    def handle_trace(self, data):
        print(data)


    # Utils

    def revome_routing_table_via(self, addr):
        self.routing_lock.acquire()
        for key, _ in self.routing_table.items():
            try:
                del self.routing_table[key][addr]
            except:
                pass

        self.routing_lock.release()
