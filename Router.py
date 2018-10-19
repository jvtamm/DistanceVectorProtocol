# https://owncloud.dcc.ufmg.br/index.php/s/3ZF96YV9JVY06CF#pdfviewer
# http://www.mathcs.emory.edu/~cheung/Courses/558/Syllabus/13-Routing/distance-vec1.html
# https://codereview.stackexchange.com/questions/83790/pydos-shell-simulation
# https://github.com/gu9/testpython-/blob/master/pg01_gu9.py
import socket, sys, json, logging, random
from collections import defaultdict as dd
from threading import Lock, Timer

logging.basicConfig(filename='example.log', filemode='w')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger().setLevel(logging.DEBUG)

class Router:
    def __init__(self, addr, period):
        self.routing_table = dd(lambda: dd(lambda: -1)) # Key -> destination addr | Value -> nextHop -> distance
        self.link_table = dict()    # Key -> destination | Value -> Weight
        self.period = period
        
        self.link_lock = Lock()
        self.routing_lock = Lock()

        self.udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp.bind((addr, 55151))

        self.timer = Timer(period, self.send_update)
        self.timer.start()

    # Command handlers

    def add_link(self, addr, weight):
        if (addr == self.udp.getsockname()[0]): sys.exit("Tried to add a link to itself")

        self.link_lock.acquire()
        self.link_table[addr] = int(weight)
        self.link_lock.release()

        logging.info(self.udp.getsockname()[0] + ' - Gateway: ' + addr + ' added to link table with weight: ' + weight)

    def remove_link(self, addr):
        self.revome_routing_table_via(addr)

        self.link_lock.acquire()
        del self.link_table[addr]
        self.link_lock.acquire()
        
        logging.info(self.udp.getsockname()[0] + ' - Gateway: ' + addr + ' removed from link table')

    def trace(self, ip):
        current_router = self.udp.getsockname()[0]
        data = {'type': "trace", 'source': current_router, 'destination': ip, 'hops':[current_router]}
        print(data)
        self.send_message(data)

    # Message type handlers

    def handle_messages(self):
        actions = {'data': self.handle_data, 'update': self.handle_update, 'trace': self.handle_trace}
        data, _ = self.udp.recvfrom(65535) 

        formated_data = json.loads(data)

        if (formated_data['type'] == 'trace'):
            print(formated_data)

        if(formated_data['type'] in actions):
            action = actions[formated_data['type']]
            action(formated_data)
    
    def handle_data(self, data):
        if (data['destination'] == self.udp.getsockname()[0]): 
            print(data['payload'])
        else:
            self.send_message(data)
            

    def handle_update(self, data):
        if (data['destination'] != self.udp.getsockname()[0]):
            print('Destination is not this router')
            return

        self.link_lock.acquire()

        logging.info(self.udp.getsockname()[0] +  ' - Handling update...')
        
        
        if (not data['source'] in self.link_table):
            print('Update message being sent through a non existing link')
            self.link_lock.release()
            return
        
        self.revome_routing_table_via(data['source'])

        self.routing_lock.acquire()

        for key, value in data['distances'].items():
            distance = int(value) + self.link_table[data['source']]
            self.routing_table[key][data['source']] = distance

        self.link_lock.release()
        self.routing_lock.release()


        self.reset_timer()

    def handle_trace(self, data):
        current_router = self.udp.getsockname()[0]
        data['hops'].append(current_router)
        print(data['hops'])
        
        if (data['destination'] == current_router):
            sending_data = {'type': 'data', 'source': current_router, 'destination': data['source'], 'payload': json.dumps(data)}
        
            self.send_message(sending_data)
        else:
            self.send_message(data)

    def send_update(self):
        self.link_lock.acquire()
        self.routing_lock.acquire()

        routes = self.routing_table.keys() | self.link_table.keys()
        
        for link in self.link_table.keys():
            data = { 'type': "update", 'source': self.udp.getsockname()[0], 'destination': link, 'distances': {} }
            for route in routes:
                if (link != route):
                    min_route, gateways = self.calculate_best_route(route)
                    for gateway in gateways:
                        if (gateway != link):
                            data['distances'][route] = min_route

            logging.info(self.udp.getsockname()[0] + ' - Sending distances: ' + str(data['distances']) + ' to brother ' + link)
            self.udp.sendto(json.dumps(data).encode('utf-8'), (link, 55151))

        self.link_lock.release()
        self.routing_lock.release()

    def send_message(self, data):
        self.routing_lock.acquire()
        self.link_lock.acquire()

        _, gateways = self.calculate_best_route(data['destination'])
        print(gateways)

        self.routing_lock.release()
        self.link_lock.release()

        if (gateways != []):
            logging.info(self.udp.getsockname()[0] + ' - Possible destinations: ' + str(gateways) + '. Randomly choosing...')
            destination = random.choice(gateways)
            logging.info(self.udp.getsockname()[0] +  ' Destination: ' + destination + ' chosen')

            self.udp.sendto(json.dumps(data).encode('utf-8'), (destination, 55151))
        else:
            logging.info(self.udp.getsockname()[0] + ' - No routes to destination: ' + data['destination'])
            # Implement error message saying that there is no route to destination

    # Utils

    def revome_routing_table_via(self, addr):
        self.routing_lock.acquire()
        for key, _ in self.routing_table.items():
            try:
                del self.routing_table[key][addr]
            except:
                pass

        self.routing_lock.release()

    def calculate_best_route(self, destination):
        min_route = sys.maxsize
        gateways = []
        
        if (destination in self.routing_table):
            routes = self.routing_table[destination].items()
            for _, value in routes:
                if(value >= 0):
                    minimum = value
                    if (minimum <= min_route): 
                        min_route = minimum
        
        if min_route != sys.maxsize:
            gateways = [key for key, value in routes if value == min_route]
        
        if (destination in self.link_table):
            if (self.link_table[destination] < min_route):
                min_route = self.link_table[destination]
                gateways = [destination]
            elif (self.link_table[destination] == min_route):
                gateways.append(destination)

        return min_route, gateways

    def reset_timer(self):
        timer = Timer(self.period, self.send_update)
        self.timer.cancel()
        self.timer = timer
        self.timer.start()

        

