import zmq
import socket
import thread
import json
import numpy as np

def getIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("192.168.0.1",80))
    ip =  s.getsockname()[0]
    s.close()
    return ip

class ZMQClient:
    def __init__(self, host, port=1980):
        try:
            addr = 'tcp://%s:%d' % (host, port)
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(addr)
            self.poller = zmq.Poller()
            self.poller.register(self.socket, zmq.POLLIN)
        except Exception as error:
            raise error

class ZMQServer:
    def __init__(self, port=1980):
        try:
            addr = 'tcp://*:%d' % (port)
            self.context = zmq.Context()
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind(addr)
        except Exception as error:
            raise error

class WifiBomb:
    def __init__(self, clients=1):
        print 'getting host address'
        host = getIP()
        print host
        print 'generating data packet'
        self.data = np.ones((1000,1000)).tolist()
        self.dump = json.dumps(self.data)
        self.server = ZMQServer()
        self.clients = [ZMQClient(host) for i in range(clients)]
        self.pollers = []
        for i in range(len(self.clients)):
            print 'generating poller #%d' % i
            p = zmq.Poller()
            p.register(self.clients[i].socket, zmq.POLLIN)
            self.pollers.append(p)

    def listen(self):
        while True:
            packet = self.server.socket.recv()
            print 'server received'
            self.server.socket.send(self.dump)
            print 'server sent'

    def run(self):
        thread.start_new_thread(self.listen, (), {})
        while True:
            try:
                for i in range(len(self.clients)):
                    self.push(self.clients[i], self.pollers[i])
            except Exception as e:
                print str(e)
            except KeyboardInterrupt:
                break
    
    def push(self, client, poller, timeout=1000):
        client.socket.send(self.dump)
        print 'client sent'
        socks = dict(poller.poll(timeout))
        if socks:
            if socks.get(client.socket) == zmq.POLLIN:
                dump = client.socket.recv(zmq.NOBLOCK)
                print 'client received'
                response = json.loads(dump)
            else:
                print 'Error: Poll Timeout'
        else:
            print 'Error: Socket Timeout'
    
if __name__ == '__main__':
    app = WifiBomb(clients=5)
    app.run()
