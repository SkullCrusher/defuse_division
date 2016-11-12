
from pprint import pprint, pformat
from time import sleep
import logging
import socket
import queue


import zeroconf as zeroconfig

from .. import concurrency
from ..concurrency import concurrent
from .. import game, net


def local_address():
    """Returns the local address of this computer."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 53))
    interface = s.getsockname()[0]
    s.close()
    return interface


def zeroconf_info():
    """zeroconf_info returns a list of tuples of the information about other
    zeroconf services on the local network. It does this by creating a
    zeroconf.ServiceBrowser and spending 0.25 seconds querying the network for
    other services."""
    ret_info = []
    def on_change(zeroconf, service_type, name, state_change):
        if state_change is zeroconfig.ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                address = "{} {}:{}".format(info.server, socket.inet_ntoa(info.address), info.port)
                props = str(info.properties.items())
                ret_info.append((address, props))
    zc = zeroconfig.Zeroconf()
    browser = zeroconfig.ServiceBrowser(zc, "_http._tcp.local.", handlers=[on_change])
    sleep(5)
    concurrency.concurrent(lambda: zc.close())()
    return ret_info



class PlayerClient(game.Conveyor):
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.stateq = queue.Queue()
        self.clientsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsock.connect((self.host, self.port))
        net.msg_recv(self.clientsock, self.stateq.put)
        conf = self.stateq.get()
        logging.debug("Conf: {}".format(conf))
        self.name = conf['name']

    def send_input(self, inpt):
        logging.debug('PlayerClient "{}" sending: {}'.format(self.name, net.json_dump(inpt)))
        self.clientsock.sendall(net.json_dump(inpt).encode('utf-8')+net.SEP)

    def get_state(self):
        return self.stateq.get()
