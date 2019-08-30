__author__ = '@sldmk'

import sys
from mainaudio import AudioTranscoder
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
    QComboBox, QGridLayout, QCheckBox, QSpinBox
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from networkServer import NetworkServer

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.windowCenter()
        self.populateDeviceList()

        self.networkServer = NetworkServer(self.spinServerPort.value())
        self.networkServer.setTranscoder(audioTranscoder)
        self.networkServer.setClientCountLabel(self.labelClientsCount)
        self.networkServer.setServerStatusLabel(self.labelServerStatus)
        self.networkServer.updateServerStatus("Server is stopped", None)

    def initUI(self):
        self.setGeometry(0, 0, 450, 350)
        self.setWindowTitle('Voice Transcoder v 0.1')
        self.startStopBtn = QPushButton("Start", self)
        self.startStopBtn.clicked.connect(self.startStopBtnClick)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.exitBtnClick)

        labelInput = QLabel('Input device:')
        labelSrvPort = QLabel('Server port:')
        self.spinServerPort = QSpinBox()
        self.spinServerPort.setMaximum(65535)
        self.spinServerPort.setMinimum(1025)
        self.spinServerPort.setValue(9518)

        labelEncodedDataTxt = QLabel('Encoded data to clients kBytes/sec: ')
        self.labelEncodedDataCount = QLabel('0')

        labelClientsTxt = QLabel('Clients count: ')
        self.labelClientsCount = QLabel('0')

        self.labelServerStatus = QLabel('Server is stopped')

        self.comboBoxInput = QComboBox(self)
        self.comboBoxOutput = QComboBox(self)
        self.comboBoxOutput.setEnabled(0)

        self.chkBoxLivePlayback = QCheckBox('Live control playback output: ')
        self.chkBoxLivePlayback.stateChanged.connect(self.chkBoxLivePlaybackClick)

        grid = QGridLayout()
        grid.setSpacing(6)

        grid.addWidget(labelInput, 1, 0)
        grid.addWidget(self.comboBoxInput, 1, 1, 1, 4)

        grid.addWidget(self.chkBoxLivePlayback, 3, 0)
        grid.addWidget(self.comboBoxOutput, 3, 1, 1, 4)

        grid.addWidget(QLabel(''), 4, 0)

        grid.addWidget(labelClientsTxt, 5, 0)
        grid.addWidget(self.labelClientsCount, 5, 1)
        grid.addWidget(labelEncodedDataTxt, 6, 0)
        grid.addWidget(self.labelEncodedDataCount, 6, 1)

        grid.addWidget(QLabel(''), 7, 0)

        grid.addWidget(self.labelServerStatus, 8, 0, 1, 4)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(labelSrvPort)
        hbox.addWidget(self.spinServerPort)
        hbox.addWidget(self.startStopBtn)
        hbox.addWidget(exitButton)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.show()

    def populateDeviceList(self):
        self.devicesIn = audioTranscoder.getAudioInputDevices()
        self.devicesOut = audioTranscoder.getAudioOutputDevices()

        for dev in self.devicesIn:
            self.comboBoxInput.addItem(self.devicesIn.get(dev))

        for dev in self.devicesOut:
            self.comboBoxOutput.addItem(self.devicesOut.get(dev))

        index = self.comboBoxInput.findText(self.devicesIn.get(audioTranscoder.getDefaultAudioInDeviceIndex()), Qt.MatchFixedString)
        if index >= 0:
            self.comboBoxInput.setCurrentIndex(index)

        index = self.comboBoxInput.findText(self.devicesIn.get(audioTranscoder.getDefaultAudioOutDeviceIndex()), Qt.MatchFixedString)
        if index >= 0:
            self.comboBoxOutput.setCurrentIndex(index)

    def getKeyByValue(self, searchDict, searchText):
        for key, value in searchDict.items():
            if value == searchText:
                return key
        return -1

    def windowCenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def exitBtnClick(self):
        if audioTranscoder.isRecordingActive:
            self.stopAudioTranscoding()
        sys.exit(0)

    def startStopBtnClick(self):
        if audioTranscoder.isRecordingActive:
            self.stopAudioTranscoding()
            self.stopNetworkServer()
            self.startStopBtn.setText('Start')
        else:
            self.startAudioTranscoding()
            self.startNetworkServer()
            self.startStopBtn.setText('Stop')
        self.spinServerPort.setEnabled(not audioTranscoder.isRecordingActive)
        self.chkBoxLivePlayback.setEnabled(not audioTranscoder.isRecordingActive)

    def stopNetworkServer(self):
        self.networkServer.stopTCPListener()

    def startNetworkServer(self):
        self.networkServer.startTCPListener()

    def updateWorkStats(self, **kwargs):
        opusBytes = kwargs.get('opusBytes', '0')
        self.labelEncodedDataCount.setText(opusBytes)

    def chkBoxLivePlaybackClick(self):
        self.comboBoxOutput.setEnabled(self.chkBoxLivePlayback.isChecked())

    def stopAudioTranscoding(self):
        audioTranscoder.stopRec()

    def startAudioTranscoding(self):
        idxDevIn = self.getKeyByValue(self.devicesIn, self.comboBoxInput.currentText())
        idxDevOut = -1

        if self.chkBoxLivePlayback.isChecked():
            idxDevOut = self.getKeyByValue(self.devicesOut, self.comboBoxOutput.currentText())

        audioTranscoder.startRec(idxDevIn, idxDevOut)

if __name__ == '__main__':
    audioTranscoder = AudioTranscoder()
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())