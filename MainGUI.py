import threading

from PyQt5.QtGui import QFont, QPalette, QColor

__author__ = '@sldmk'

import sys
from mainaudio import AudioRecorder
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
    QComboBox, QGridLayout, QCheckBox
from PyQt5.QtCore import Qt

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.redColorPalette = QPalette()
        self.greenColorPalette = QPalette()
        self.redColorPalette.setColor(QPalette.WindowText, QColor("red"))
        self.greenColorPalette.setColor(QPalette.WindowText, QColor("green"))

        self.initUI()
        self.windowCenter()
        self.populateDeviceList()

    def initUI(self):
        self.setGeometry(0, 0, 450, 350)
        self.setWindowTitle('Voice Transcoder v 0.1')
        self.startStopBtn = QPushButton("Start", self)
        self.startStopBtn.clicked.connect(self.startStopBtnClick)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.exitBtnClick)

        labelInput = QLabel('Input device:')

        labelEncodedDataTxt = QLabel('Encoded data to clients kBytes/sec: ')
        self.labelEncodedDataCount = QLabel('0')

        labelClientsTxt = QLabel('Clients count: ')
        self.labelClientsCount = QLabel('0')

        self.labelServerReadyStatus = QLabel('Server not ready')
        self.labelServerReadyStatus.setPalette(self.redColorPalette)

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

        grid.addWidget(self.labelServerReadyStatus, 8, 0)

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

    def populateDeviceList(self):
        self.devicesIn = audioRecorder.getAudioInputDevices()
        self.devicesOut = audioRecorder.getAudioOutputDevices()

        for dev in self.devicesIn:
            self.comboBoxInput.addItem(self.devicesIn.get(dev))

        for dev in self.devicesOut:
            self.comboBoxOutput.addItem(self.devicesOut.get(dev))

        index = self.comboBoxInput.findText(self.devicesIn.get(audioRecorder.getDefaultAudioInDeviceIndex()), Qt.MatchFixedString)
        if index >= 0:
            self.comboBoxInput.setCurrentIndex(index)

        index = self.comboBoxInput.findText(self.devicesIn.get(audioRecorder.getDefaultAudioOutDeviceIndex()), Qt.MatchFixedString)
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
        if audioRecorder.isRecordingActive:
            self.stopAudioTranscoding()
        sys.exit(0)

    def startStopBtnClick(self):
        if audioRecorder.isRecordingActive:
            self.stopAudioTranscoding()
        else:
            self.startAudioTranscoding()

    def updateWorkStats(self, **kwargs):
        opusBytes = kwargs.get('opusBytes', '0')
        self.labelEncodedDataCount.setText(opusBytes)

    def chkBoxLivePlaybackClick(self):
        self.comboBoxOutput.setEnabled(self.chkBoxLivePlayback.isChecked())

    def stopAudioTranscoding(self):
        audioRecorder.stopRec()
        self.startStopBtn.setText('Start')

    def startAudioTranscoding(self):
        idxDevIn = self.getKeyByValue(self.devicesIn, self.comboBoxInput.currentText())
        idxDevOut = -1

        if self.chkBoxLivePlayback.isChecked():
            idxDevOut = self.getKeyByValue(self.devicesOut, self.comboBoxOutput.currentText())

        audioRecorder.startRec(idxDevIn, idxDevOut)
        self.startStopBtn.setText('Stop')

if __name__ == '__main__':
    audioRecorder = AudioRecorder()
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())