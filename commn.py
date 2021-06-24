import socket, threading, time, json
import inspect, traceback, keyboard

servers = list()
emmA = False

def encode(data):
    return bytes(data+"|", "utf-8")

def decode(data):
    return data.decode("utf-8").split("|")

def closeOnERR(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            for server in servers:
                server.close()
            #print(f"{type(e).__name__}: {e}")
            print(traceback.format_exc())
            print("Closing server")
    return inner

def emmAbort():
    global emmA
    if not emmA:
        print("You're are using the emmergency abort\nPress ctrl+alt to abort\nWARNING: Do not use in production\n")
        def innerAbort():
            keyboard.wait("ctrl+alt")

            for server in servers:
                server.close()
                print("server aborted")
                
        t = threading.Thread(target=innerAbort, args=())
        t.daemon = True
        t.start()
        emmA = True

class SocketServer():
    def __init__(self, HOST="127.0.0.1", PORT=8000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((HOST, PORT))
        self.sock.listen()
        self._thConn()
        #self.conns = dict()
        self.consumers = dict()
        servers.append(self)

    def _thConn(self):
        t = threading.Thread(target=self._connGK, args=())
        t.start()

    def _connGK(self): # connection gatekeeper
        try:
            conn, addr = self.sock.accept()
        except OSError:
            return None
        self._thConn()
        #self.conns[conn] = addr
        DIR = decode(conn.recv(1024))[0]
        if not DIR in self.consumers:
            self.send(conn, "The direction {DIR} does not exists")
            self.reject(conn)
            return None
        self.consumers[DIR].conns[conn] = addr
        self.connect(conn, DIR)
        self.consumers[DIR].connect(conn)
        close = False
        while not close:
            close = self._mIn(conn, DIR)

    def _mIn(self, conn, DIR): # messgae in
        r = True
        message = b""
        try:
            message = conn.recv(1024)
        except OSError:
            r = False #return True
        except Exception as e:
            print(traceback.format_exc())
            #print(f"{type(e).__name__}: {e}")

        if message:
            message = decode(message)
            for data in message:
                if data:
                    self.receive(conn, data, DIR)
                    self.consumers[DIR].receive(conn, data)
            return False
        
        self.disconnect(conn, DIR)
        self.consumers[DIR].disconnect(conn)
        self.consumers[DIR].conns.pop(conn)
        if r: self.reject(conn)
        return True

    def connect(self, conn, DIR):
        pass

    def disconnect(self, conn, DIR):
        pass

    def receive(self, conn, data, DIR):
        pass

    def send(self, conn, data):
        conn.sendall(encode(data))

    def reject(self, conn):
        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        #self.conns.pop(conn)     

    def close(self):
        self.sock.close()
        servers.remove(self)


class SocketConsumer():
    def __init__(self, server=None, DIR="default"):
        self.dir = DIR
        self.server = server
        if self.dir in self.server.consumers:
            self.server.close()
            raise RuntimeError(f"The direction {self.dir} is already taken")
        self.server.consumers[self.dir] = self
        self.conns = dict()

    def connect(self, conn):
        pass

    def disconnect(self, conn):
        pass

    def receive(self, conn, data):
        pass

    def send(self, conn, data):
        self.server.send(conn, data)

    def close(self):
        for conn in self.conns:
            self.server.reject(conn)
        self.server.consumers.pop(self.dir)


class SocketClient(): # ConnectionAbortedError, ConnectionRefusedError
    def __init__(self, HOST="127.0.0.1", PORT=8000, DIR="default"):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        self.send(DIR)
        t = threading.Thread(target=self._mIn, args=())
        t.start()
        self.connect()

    def _mIn(self):
        while True:
            try:
                message = decode(self.sock.recv(1024))
            except OSError:
                break
            for data in message:
                if data:
                    self.receive(data)

    def connect(self):
        pass

    def disconnect(self):
        pass
        
    def receive(self, data):
        pass

    def send(self, data): # only accepts strings
        self.sock.sendall(encode(data))

    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.disconnect()

