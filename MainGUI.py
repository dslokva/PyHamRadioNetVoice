from PyQt5.QtGui import QColor, QPalette

__author__ = '@sldmk'

import sys
from mainaudio import AudioTranscoder
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
    QComboBox, QGridLayout, QCheckBox, QSpinBox, QLCDNumber, QSlider
from PyQt5.QtCore import Qt
from networkServer import NetworkServer

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.greenColorPalette = QPalette()
        self.greenColorPalette.setColor(QPalette.WindowText, QColor("green"))
        self.blackColorPalette = QPalette()
        self.blackColorPalette.setColor(QPalette.WindowText, QColor("black"))

        self.initUI()
        self.windowCenter()
        self.devicesIn = None
        self.devicesOut = None
        self.populateDeviceList()

        self.networkServer = NetworkServer()
        self.networkServer.setTranscoder(audioTranscoder)
        self.networkServer.setClientCountLabel(self.labelClientsCount)
        self.networkServer.setServerStatusLabel(self.labelServerStatus)
        self.networkServer.setEncodedDataCountLabel(self.labelEncodedDataCount)
        self.networkServer.updateServerStatus("Server is stopped", None)

    def initUI(self):
        self.setGeometry(0, 0, 450, 400)
        self.setWindowTitle('Voice Transcoder server v 0.1')
        self.startStopBtn = QPushButton("Start", self)
        self.startStopBtn.clicked.connect(self.startStopBtnClick)

        exitButton = QPushButton("Exit")
        exitButton.clicked.connect(self.exitBtnClick)


        self.labelSrvPort = QLabel('Server port:')
        self.spinServerPort = QSpinBox()
        self.spinServerPort.setMaximum(65535)
        self.spinServerPort.setMinimum(1025)
        self.spinServerPort.setValue(9518)

        labelEncodedDataTxt = QLabel('Encoded data to clients kBytes/sec: ')
        self.labelEncodedDataCount = QLabel('0')

        labelClientsTxt = QLabel('Clients count: ')
        self.labelClientsCount = QLabel('0')

        self.labelBitrate = QLabel('OPUS bitrate: ')
        self.comboBoxBitrate = QComboBox(self)
        self.comboBoxBitrate.addItems(["8000", "12000", "24000", "48000"])
        self.comboBoxBitrate.activated[str].connect(self.comboBoxBitrateChange)
        self.comboBoxBitrate.setCurrentIndex(2)

        labelVolume = QLabel('Volume gain:')
        self.labelVolumeValue = QLabel('0%')
        self.labelVolumeValue.setAlignment(Qt.AlignCenter)
        self.sliderVolume = QSlider(Qt.Horizontal)
        self.sliderVolume.setTickPosition(QSlider.TicksBothSides)
        self.sliderVolume.setMinimum(10)
        self.sliderVolume.setMaximum(20)
        self.sliderVolume.setTickInterval(1)
        self.sliderVolume.setSingleStep(1)
        self.sliderVolume.valueChanged.connect(self.volumeChangeEvent)

        self.labelServerStatus = QLabel('Server is stopped')

        self.labelInput = QLabel('Input device:')
        self.comboBoxInput = QComboBox(self)
        self.comboBoxOutput = QComboBox(self)
        self.comboBoxOutput.setEnabled(0)

        self.chkBoxLivePlayback = QCheckBox('Live control playback output: ')
        self.chkBoxLivePlayback.stateChanged.connect(self.chkBoxLivePlaybackClick)

        self.labelLcdTrxFrequency = QLabel('Transceiver frequency:')
        self.lcdTrxFrequency = QLCDNumber(9)
        self.lcdTrxFrequency.display('14.150.00')
        self.lcdTrxFrequency.setPalette(self.blackColorPalette)
        self.lcdTrxFrequency.setMinimumHeight(48)

        grid = QGridLayout()
        grid.setSpacing(6)

        grid.addWidget(self.labelInput, 1, 0)
        grid.addWidget(self.comboBoxInput, 1, 1, 1, 5)

        grid.addWidget(self.chkBoxLivePlayback, 3, 0)
        grid.addWidget(self.comboBoxOutput, 3, 1, 1, 5)

        grid.addWidget(self.labelBitrate, 4, 0)
        grid.addWidget(self.comboBoxBitrate, 4, 1, 1, 5)

        grid.addWidget(labelVolume, 5, 0)
        grid.addWidget(self.sliderVolume, 5, 1, 1, 4)
        grid.addWidget(self.labelVolumeValue, 5, 5)

        grid.addWidget(QLabel(''), 6, 0)

        grid.addWidget(labelClientsTxt, 7, 0)
        grid.addWidget(self.labelClientsCount, 7, 1)
        grid.addWidget(labelEncodedDataTxt, 8, 0)
        grid.addWidget(self.labelEncodedDataCount, 8, 1)

        grid.addWidget(QLabel(''), 9, 0)

        grid.addWidget(self.labelServerStatus, 10, 0, 1, 5)

        grid.addWidget(QLabel(''), 11, 0)

        grid.addWidget(self.labelLcdTrxFrequency, 12, 0, 1, 2)
        grid.addWidget(self.lcdTrxFrequency, 12, 1, 1, 5)

        grid.addWidget(QLabel(''), 13, 0)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.labelSrvPort)
        hbox.addWidget(self.spinServerPort)
        hbox.addWidget(self.startStopBtn)
        hbox.addWidget(exitButton)

        vbox = QVBoxLayout()
        vbox.addLayout(grid)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setMinimumSize(450, 400)
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

    def comboBoxBitrateChange(self, text):
        audioTranscoder.setBitrate(int(text))

    def exitBtnClick(self):
        if audioTranscoder.isRecordingActive:
            self.stopAudioTranscoding()
            self.stopNetworkServer()
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
        self.labelSrvPort.setEnabled(not audioTranscoder.isRecordingActive)
        self.labelBitrate.setEnabled(not audioTranscoder.isRecordingActive)
        self.comboBoxBitrate.setEnabled(not audioTranscoder.isRecordingActive)
        self.labelInput.setEnabled(not audioTranscoder.isRecordingActive)
        self.comboBoxInput.setEnabled(not audioTranscoder.isRecordingActive)

    def stopNetworkServer(self):
        self.networkServer.stopTCPListener()

    def startNetworkServer(self):
        self.networkServer.startTCPListener(self.spinServerPort.value())

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

    def volumeChangeEvent(self):
        self.labelVolumeValue.setText(str((self.sliderVolume.value()*10)-100)+"%")
        audioTranscoder.setVolume(self.sliderVolume.value()*10)

if __name__ == '__main__':
    audioTranscoder = AudioTranscoder(24000)
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())