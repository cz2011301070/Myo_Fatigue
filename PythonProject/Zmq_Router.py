#
#  Client world client in python
#  Connects REQ socket to tcp://localhost:5555
#  Sends "Hello" to server, expects "World" back
#

import zmq
import struct# handles binary streams on the network. Transfers binary to any C style data type
from zmq.devices import monitored_queue

# context=zmq.Context()
# #  Socket to talk to server
# print("Connecting to hello world server>>>")
# socket=context.socket(zmq.ROUTER)
# socket.bind("tcp://127.0.0.1:5689")
# # socket.setsockopt(zmq.SUBSCRIBE, b"POSITION")

# while True:
#     try:
#         if socket.poll(timeout=1, flags= zmq.POLLIN):
#             msg = socket.recv_multipart()
#             msglen = len(msg[2])
#             ret=struct.unpack(str(msglen)+"s",msg[2])[0].decode('utf-8')#binary to string
#             print(msg)
#             print(ret)
#         # res=b'\x00\x00 A'
#         # ret = gzip.decompress(res).decode("utf-8")
#         # ret=int.from_bytes(msg[1],byteorder="big",signed=False)
#         # ret=struct.unpack("f",msg[1])[0]#binary to float
#         # print(msg)
#     except zmq.ZMQError as e:
#         if e.errno == zmq.ETERM:
#             break           # Interrupted
#         else:
#             raise

class ZmqRouter:
    def __init__(self,address):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(address)
    def PollData(self):
        try:
            if self.socket.poll(timeout=1, flags= zmq.POLLIN):
                msg = self.socket.recv_multipart()
                msglen = len(msg[2])
                ret=struct.unpack(str(msglen)+"s",msg[2])[0].decode('utf-8')#binary to string
                return ret
            else:
                return "NAN"
        except zmq.ZMQError as e:
            raise



# #Do 10 requests, waiting each time for a response
# for request in range(10):
#     print("sending request %s ..." % request)
#     socket.send(b"hello")

#     #Get the reply
#     message = socket.recv()
#     print("Reveived reply %s [%s]" % (request, message))






