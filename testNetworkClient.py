import random

from PyQt5.QtGui import QPalette, QColor

__author__ = '@sldmk'

import sys
from PyQt5.QtCore import Qt
from threading import Thread, Timer
import socket
import pyaudio
from pyaudio import Stream
from OPUSCodecImpl import OpusCodec
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
    QComboBox, QGridLayout, QSpinBox, QLineEdit, QCheckBox


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.windowCenter()
        self.devicesOut = None
        self.clientTCPSocket = None
        self.populateDeviceList()
        audioPlayer.setAverageDataLabel(self.labelEncodedDataCount)

    def initUI(self):
        self.redColorPalette = QPalette()
        self.greenColorPalette = QPalette()
        self.redColorPalette.setColor(QPalette.WindowText, QColor("red"))
        self.greenColorPalette.setColor(QPalette.WindowText, QColor("green"))

        self.setGeometry(0, 0, 450, 250)
        self.setWindowTitle('Voice Transcoder client v 0.1')
        self.startStopBtn = QPushButton("Connect and play", self)
        self.startStopBtn.clicked.connect(self.startStopBtnClick)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.exitBtnClick)

        self.labelServerAddr = QLabel('Server address:')
        self.labelServerPort = QLabel('Server port:')

        self.txtServerAddr = QLineEdit('192.168.1.103')
        self.spinServerPort = QSpinBox()
        self.spinServerPort.setMaximum(65535)
        self.spinServerPort.setMinimum(1025)
        self.spinServerPort.setValue(9518)

        self.chkBoxfixedClientPort = QCheckBox('Fixed client UDP port:')
        self.chkBoxfixedClientPort.stateChanged.connect(self.chkBoxfixedClientPortClick)

        self.spinClientPort = QSpinBox()
        self.spinClientPort.setMaximum(65535)
        self.spinClientPort.setMinimum(1025)
        random.seed()
        self.spinClientPort.setValue(random.randint(10000, 65535))
        self.spinClientPort.setEnabled(False)

        labelEncodedDataTxt = QLabel('Encoded data from server kBytes/sec: ')
        self.labelEncodedDataCount = QLabel('0')

        self.labelClientStatus = QLabel('Client is stopped')
        self.labelClientStatus.setPalette(self.redColorPalette)

        self.labelOutput = QLabel('Output device: ')
        self.comboBoxOutput = QComboBox(self)

        grid = QGridLayout()
        grid.setSpacing(6)

        grid.addWidget(self.labelOutput, 0, 0)
        grid.addWidget(self.comboBoxOutput, 0, 1, 1, 4)

        grid.addWidget(QLabel(''), 1, 0)

        grid.addWidget(self.labelServerAddr, 2, 0, 1, 2)
        grid.addWidget(self.txtServerAddr, 2, 2)

        grid.addWidget(self.labelServerPort, 3, 0, 1, 2)
        grid.addWidget(self.spinServerPort, 3, 2)

        grid.addWidget(self.chkBoxfixedClientPort, 4, 0, 1, 2)
        grid.addWidget(self.spinClientPort, 4, 2)

        grid.addWidget(QLabel(''), 5, 0)

        grid.addWidget(labelEncodedDataTxt, 6, 0, 1, 2)
        grid.addWidget(self.labelEncodedDataCount, 6, 2)

        grid.addWidget(QLabel(''), 7, 0)

        grid.addWidget(self.labelClientStatus, 8, 0, 1, 4)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.startStopBtn)
        hbox.addWidget(exitButton)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()

    def chkBoxfixedClientPortClick(self):
        self.spinClientPort.setEnabled(self.chkBoxfixedClientPort.isChecked())

    def windowCenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def populateDeviceList(self):
        self.devicesOut = audioPlayer.getAudioOutputDevices()

        for dev in self.devicesOut:
            self.comboBoxOutput.addItem(self.devicesOut.get(dev))

        index = self.comboBoxOutput.findText(self.devicesOut.get(audioPlayer.getDefaultAudioOutDeviceIndex()), Qt.MatchFixedString)
        if index >= 0:
            self.comboBoxOutput.setCurrentIndex(index)

    def exitBtnClick(self):
        if audioPlayer.isActive:
            self.stopAudioTranscoding()
        sys.exit(0)

    def startStopBtnClick(self):
        if audioPlayer.isActive:
            self.stopAudioPlaying()
            self.startStopBtn.setText('Connect and play')
        else:
            self.startAudioPlaying()
            self.startStopBtn.setText('Stop')
        self.labelOutput.setEnabled(not audioPlayer.isActive)
        self.comboBoxOutput.setEnabled(not audioPlayer.isActive)
        self.labelServerAddr.setEnabled(not audioPlayer.isActive)
        self.txtServerAddr.setEnabled(not audioPlayer.isActive)
        self.labelServerPort.setEnabled(not audioPlayer.isActive)
        self.spinServerPort.setEnabled(not audioPlayer.isActive)
        self.chkBoxfixedClientPort.setEnabled(not audioPlayer.isActive)
        self.spinClientPort.setEnabled(not audioPlayer.isActive and self.chkBoxfixedClientPort.isChecked())

    def startAudioPlaying(self):
        idxDevOut = self.getKeyByValue(self.devicesOut, self.comboBoxOutput.currentText())
        if self.connectToServer(self.txtServerAddr.text(), self.spinServerPort.value()):
            audioPlayer.startRecv(idxDevOut, self.spinClientPort.value())
            self.labelClientStatus.setPalette(self.greenColorPalette)

    def stopAudioPlaying(self):
        try:
            audioPlayer.stopRecv()
            self.clientTCPSocket.send('stopstream=true'.encode())
            self.clientTCPSocket.close()
            self.labelClientStatus.setText('Client is stopped')
            self.labelClientStatus.setPalette(self.redColorPalette)
        except Exception as err:
            print(str(err))

    def connectToServer(self, address, port):
        try:
            # Create a socket connection for connecting to the server:
            self.clientTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientTCPSocket.connect((address, port))

            # send hello to server
            initialHello = socket.gethostname() + ('|type=hello|version=1.0')
            self.clientTCPSocket.send(initialHello.encode())

            # receive server first reply
            reply = self.clientTCPSocket.recv(1024).decode()
            print(reply)

            selectedUDPPort = 'udpport=' + str(self.spinClientPort.value())
            self.clientTCPSocket.send(selectedUDPPort.encode())
            self.labelClientStatus.setText('Connected to server: '+address)
            return True
        except socket.error as err:
            self.labelClientStatus.setText(err.strerror)
            return False

    def getKeyByValue(self, searchDict, searchText):
        for key, value in searchDict.items():
            if value == searchText:
                return key
        return -1

class StreamAudioPlayer():
    def __init__(self):
        self.isActive = False
        self.audioOut = pyaudio.PyAudio()
        self.info = self.audioOut.get_host_api_info_by_index(0)
        self.numdevices = self.info.get('deviceCount')
        self.idxDevOut = 0
        self.dataLst = []
        self.labelAverageDataCount = QLabel
        self.streamOut = Stream(self, rate=48000, channels=1, format=pyaudio.paInt16, input=False, output=True)
        self.streamOut.stop_stream()

        self.codec = OpusCodec(channels=1, rate=48000, frame_size=3840)

    def startRecv(self, devOut, udpPort):
        chunk = 3840
        self.isActive = True
        self.streamOut = self.audioOut.open(format=pyaudio.paInt16, channels=1,
                                            rate=48000, input=False, output=True,
                                            output_device_index=devOut,
                                            frames_per_buffer=3840)
        Thread(target=self.udpStream, args=(chunk, udpPort)).start()
        Timer(1.0, function=self.calculateAverage).start()

    def stopRecv(self):
        self.isActive = False
        self.streamOut.stop_stream()

    def calculateAverage(self):
        # print(round(sum(self.dataLst) / 1024, 2))
        self.labelAverageDataCount.setText(str(round(sum(self.dataLst) / 1024, 2)))
        self.dataLst = []
        if self.isActive:
            Timer(1.0, function=self.calculateAverage).start()
        else:
            self.labelAverageDataCount.setText('0')

    def udpStream(self, chunk, udpPort):
        udpReceiveSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpReceiveSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpReceiveSocket.bind(("192.168.1.103", udpPort))

        while self.isActive:
            soundData, addr = udpReceiveSocket.recvfrom(chunk)
            if len(soundData) > 100:
                self.dataLst.append(len(soundData))
                opusdecoded_data = self.codec.decode(soundData)
                self.streamOut.write(opusdecoded_data)
        udpReceiveSocket.close()
        print("socket closed")

    def getDefaultAudioOutDeviceIndex(self):
        return self.audioOut.get_default_output_device_info()["index"]

    def getAudioOutputDevices(self):
        devices = {}
        for i in range(0, self.numdevices):
            devOut = self.audioOut.get_device_info_by_host_api_device_index(0, i)
            if (devOut.get('maxOutputChannels')) > 0:
                d = {devOut.get('index'): devOut.get('name')}
                devices.update(d)
        return devices

    def setAverageDataLabel(self, label):
        self.labelAverageDataCount = label

if __name__ == '__main__':
    app = QApplication(sys.argv)
    audioPlayer = StreamAudioPlayer()
    ex = MainWindow()
    sys.exit(app.exec_())



