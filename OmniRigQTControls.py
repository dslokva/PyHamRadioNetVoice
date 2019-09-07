from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QLabel, QGroupBox, QRadioButton, QHBoxLayout, QLCDNumber, QVBoxLayout, QGridLayout


class OmniRigQTControls:
    def __init__(self):
        self.blackColorPalette = QPalette()
        self.blackColorPalette.setColor(QPalette.WindowText, QColor("black"))
        self.redColorPalette = QPalette()
        self.redColorPalette.setColor(QPalette.WindowText, QColor("red"))

        self.labelRigName = QLabel("Rig is not responding")
        self.rigSelectGroupBox = QGroupBox("Rig select:")
        self.radioBtnTRX1 = QRadioButton("Rig 1")
        self.radioBtnTRX1.setChecked(True)
        self.radioBtnTRX2 = QRadioButton("Rig 2")

        hboxRigSelect = QHBoxLayout()
        hboxRigSelect.addWidget(self.radioBtnTRX1)
        hboxRigSelect.addWidget(self.radioBtnTRX2)
        self.rigSelectGroupBox.setLayout(hboxRigSelect)

        self.lcdTrxFrequency = QLCDNumber(9)
        self.lcdTrxFrequency.display('00.000.00')
        self.lcdTrxFrequency.setPalette(self.blackColorPalette)
        self.lcdTrxFrequency.setMinimumHeight(50)
        self.lcdTrxFrequency.setMaximumHeight(50)
        self.lcdTrxFrequency.setMaximumWidth(275)

        self.vboxMainLayout = QVBoxLayout()
        self.vboxMainLayout.addWidget(self.rigSelectGroupBox)
        self.vboxMainLayout.addWidget(self.lcdTrxFrequency)
        self.vboxMainLayout.addWidget(self.labelRigName)

        self.grid = QGridLayout()
        self.grid.setSpacing(3)

        self.grid.addWidget(self.rigSelectGroupBox, 1, 0)
        self.grid.addWidget(self.lcdTrxFrequency, 1, 1, 1, 5)
        self.grid.addWidget(self.labelRigName, 2, 0, 1, 1)

    def setDisplayFreq(self, txtFreq):
        self.lcdTrxFrequency.display(txtFreq)

    def setOmniRigErrorText(self, msgText):
        self.labelRigName.setText(msgText)
        self.labelRigName.setPalette(self.redColorPalette)

    def setRigStatus(self, rigType):
        self.labelRigName.setText(rigType)
        self.labelRigName.setPalette(self.blackColorPalette)

    def disableControls(self):
        self.radioBtnTRX1.setEnabled(False)
        self.radioBtnTRX2.setEnabled(False)

    def refreshRigInformation(self, omniRigInfo):
        rignum = 2
        if self.radioBtnTRX1.isChecked():
            rignum = 1
        self.setDisplayFreq(self.addDotsToFreq(omniRigInfo[rignum].getRigFreq()))
        self.setRigStatus(omniRigInfo[rignum].getRigType() + ": " + omniRigInfo[rignum].getRigStatus())

    def addDotsToFreq(self, freqvalue):
        freqTxt = str(freqvalue)
        print(freqTxt)
        mainPart = freqTxt[:7]
        firstPar = freqTxt[:-6]
        middlePart = mainPart[1:4]
        lastPart = mainPart[4:]
        print(firstPar)
        # middlePart = freqTxt[3:]
        # newTxt = freqTxt[len(freqTxt)-5:]+"."+middlePart+"."+lastPart
        return firstPar+"."+middlePart+"."+lastPart

    def getGUI(self):
        return self.grid

