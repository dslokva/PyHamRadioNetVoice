from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QLabel

__author__ = '@sldmk'

from threading import Thread, Timer
import socket

class NetworkServer:
    def __init__(self):
        self.port = 9518
        self.isServerActive = False
        self.transcoder = None
        self.UDPSockets = {}
        self.clientsCountLabel = QLabel()
        self.serverStatusLabel = QLabel()
        self.encodedDataCountLabel = QLabel()

        self.redColorPalette = QPalette()
        self.greenColorPalette = QPalette()
        self.redColorPalette.setColor(QPalette.WindowText, QColor("red"))
        self.greenColorPalette.setColor(QPalette.WindowText, QColor("green"))

    def stopTCPListener(self):
        self.isServerActive = False
        self.server_socket.close()
        self.updateServerStatus("Server is stopped", self.redColorPalette)

    def startTCPListener(self, port):
        self.isServerActive = True
        self.port = port
        tcpListenerThread = Thread(target=self.TCPListener)
        tcpListenerThread.setDaemon(True)
        tcpListenerThread.start()
        Timer(1.0, function=self.calculateAverage).start()

    def TCPListener(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        self.updateServerStatus("Server is ready and waiting for clients at " + self.get_default_ip_address() + ":" + str(self.port), self.greenColorPalette)

        while self.isServerActive:
            try:
                client_socket, address = self.server_socket.accept()
                Thread(target=self.handleNetworkTCPClient, args=(address, client_socket)).start()
            except socket.error as msg:
                print("Server socket exception: %s" % msg)

    def setClientCountLabel(self, label):
        self.clientsCountLabel = label

    def updateClientCount(self):
        self.clientsCountLabel.setText(str(self.transcoder.getUDPStreamsCount()))

    def setServerStatusLabel(self, label):
        self.serverStatusLabel = label

    def setEncodedDataCountLabel(self, label):
        self.encodedDataCountLabel = label

    def updateServerStatus(self, status, palette):
        self.serverStatusLabel.setText(status)
        if palette is None:
            palette = self.redColorPalette
        self.serverStatusLabel.setPalette(palette)

    def calculateAverage(self):
        self.encodedDataCountLabel.setText(str(round(sum(self.transcoder.getDataLst()) / 1024, 2)))
        self.transcoder.clearDataLst()

        if self.isServerActive:
            Timer(1.0, function=self.calculateAverage).start()
        else:
            self.encodedDataCountLabel.setText('0')

    def handleNetworkTCPClient(self, address, client_tcp_socket):
        while self.isServerActive:
            try:
                if client_tcp_socket._closed is False:
                    clienttext = client_tcp_socket.recv(1024).decode()
                    if clienttext.find("type=hello", 0, len(clienttext)) != -1:
                        print("Client connected: ", clienttext, ", from: ", address[0], ":", address[1])
                        client_tcp_socket.send('type=ready|request=udpport'.encode())

                    if clienttext.find("udpport", 0, len(clienttext)) != -1:
                        clientUDPPort = clienttext.partition("=")[2]
                        print("Client UDP port: ", clientUDPPort)
                        client_tcp_socket.send(str('setbitrate='+str(self.transcoder.getBitrate())).encode())
                        client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        self.transcoder.addUDPClient(str(address[0]+":"+clientUDPPort), client_udp_socket)
                        self.updateClientCount()

                    if clienttext.find("stopstream", 0, len(clienttext)) != -1:
                        print("Client socket terminate: "+str(address[0]))
                        client_tcp_socket.close()
                        self.transcoder.removeUDPClient(str(address[0]))
                        self.updateClientCount()
                else:
                    self.transcoder.removeUDPClient(str(address[0]))
                    self.updateClientCount()
                    break

            except socket.error as msg:
                print("Client socket exception: %s\n" % msg)
                client_tcp_socket.close()
                self.transcoder.removeUDPClient(str(address[0]))
                self.updateClientCount()
        client_tcp_socket.close()

    def get_default_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    def setTranscoder(self, coder):
        self.transcoder = coder