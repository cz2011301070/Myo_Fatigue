import zmq
import struct# handles binary streams on the network. Transfers binary to any C style data type
from zmq.devices import monitored_queue


class ZmqDealer:
    def __init__(self,address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.connect(address)
    def send(self, content:str):
        self.socket.send_multipart([b"Zhuang", content.encode()])
        









