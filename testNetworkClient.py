__author__ = '@sldmk'

from threading import Thread
import socket
import pyaudio
from pyaudio import Stream
from OPUSCodecImpl import OpusCodec


class PlayStream:
    def __init__(self):
        self.audioOut = pyaudio.PyAudio()
        self.streamOut = Stream(self, rate=48000, channels=1, format=pyaudio.paInt16, input=False, output=True)
        self.streamOut.stop_stream()
        self.codec = OpusCodec(channels=1, rate=48000, frame_size=3840)
        self.streamOut = self.audioOut.open(format=pyaudio.paInt16, channels=1,
                                            rate=48000, input=False, output=True,
                                            output_device_index=4,
                                            frames_per_buffer=3840)

    def startRecv(self):
        chunk = 3840
        Thread(target=self.udpStream, args=(chunk,)).start()

    def udpStream(self, chunk):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(("127.0.0.1", 12345))

        while True:
            soundData, addr = udp.recvfrom(chunk)
            if soundData:
                opusdecoded_data = self.codec.decode(soundData)
                self.streamOut.write(opusdecoded_data)


port = 9518
ip = "10.4.67.20"

# Create a socket connection for connecting to the server:
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((ip, port))

# send hello to server
initialHello = socket.gethostname()+('|type=hello|version=1.0')
client_socket.send(initialHello.encode())

# receive server first reply
reply = client_socket.recv(1024).decode()
print(reply)
selectedUDPPort = 'udpport=12345'

playstream = PlayStream()
playstream.startRecv()

client_socket.send(selectedUDPPort.encode())



