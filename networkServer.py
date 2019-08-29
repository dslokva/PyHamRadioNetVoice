__author__ = '@sldmk'

from threading import Thread
import socket

class NetworkServer:
    def __init__(self, port):
        self.port = port
        self.isServerActive = False

    def stopTCPListener(self):
        self.isServerActive = False
        self.server_socket.close()

    def startTCPListener(self):
        self.isServerActive = True
        tcpListenerThread = Thread(target=self.TCPListener)
        tcpListenerThread.setDaemon(True)
        tcpListenerThread.start()

    def TCPListener(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)

        print("Waiting for clients at: ", self.get_default_ip_address(),":",self.port)
        while self.isServerActive:
            try:
                client_socket, address = self.server_socket.accept()
                Thread(target=self.handleNetworkTCPClient, args=(address, client_socket)).start()
            except socket.error as msg:
                print("Server socket exception: %s" % msg)

    def handleNetworkTCPClient(self, address, client_socket):
        while self.isServerActive:
            try:
                clienttext = client_socket.recv(1024).decode()
                if clienttext.find("type=hello", 0, len(clienttext)) != -1:
                    print("Client connected: ", clienttext, ", from: ", address[0], ":", address[1])
                    client_socket.send('type=ready|request=udpport'.encode())
                if clienttext.find("udpport", 0, len(clienttext)) != -1:
                    print("Client UDP port: ", clienttext.partition("=")[2])


            except socket.error as msg:
                print("Client socket exception: %s" % msg)
        client_socket.close()

    # def udpStreamToClient(self):
    #     udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     while True:
    #         udp.sendto(opusdata, ("127.0.0.1", 12345))
    #     udp.close()

    def get_default_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
