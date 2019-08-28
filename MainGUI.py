from cybox.test import dev

__author__ = '@sldmk'

import sys
from mainaudio import AudioRecorder
from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, \
    QComboBox, QGridLayout
from PyQt5.QtCore import Qt

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
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
        labelOutput = QLabel('Output device')

        self.comboBoxInput = QComboBox(self)
        self.comboBoxOutput = QComboBox(self)

        grid = QGridLayout()
        grid.setSpacing(5)

        grid.addWidget(labelInput, 1, 0)
        grid.addWidget(self.comboBoxInput, 1, 1, 1, 4)

        grid.addWidget(labelOutput, 2, 0)
        grid.addWidget(self.comboBoxOutput, 2, 1, 1, 4)

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
        devicesIn = audioRecorder.getAudioInputDevices()
        devicesOut = audioRecorder.getAudioOutputDevices()

        for dev in devicesIn:
            self.comboBoxInput.addItem(devicesIn.get(dev))

        for dev in devicesOut:
            self.comboBoxOutput.addItem(devicesOut.get(dev))

        print(audioRecorder.getDefaultAudioInDeviceIndex())
        print(audioRecorder.getDefaultAudioOutDeviceIndex())

    def windowCenter(self):
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def exitBtnClick(self):
        sys.exit(0)

    def startStopBtnClick(self):
        if audioRecorder.recordingIsActive:
            audioRecorder.stopRec()
            self.startStopBtn.setText('Start')
        else:
            audioRecorder.startRec()
            self.startStopBtn.setText('Stop')

if __name__ == '__main__':
    audioRecorder = AudioRecorder()
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())