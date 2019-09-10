from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QLabel, QGroupBox, QRadioButton, QHBoxLayout, QLCDNumber, QVBoxLayout, QGridLayout, \
    QPushButton


class OmniRigQTControls:
    def __init__(self, operatingAsClient):
        self.operatingAsClient = operatingAsClient
        self.omnirigObject = None
        self.omniRigInfo = {}
        self.blackColorPalette = QPalette()
        self.blackColorPalette.setColor(QPalette.WindowText, QColor("black"))
        self.redColorPalette = QPalette()
        self.redColorPalette.setColor(QPalette.WindowText, QColor("red"))
        self.boldFont = QFont()
        self.boldFont.setBold(True)
        self.regularFont = QFont()
        self.regularFont.setBold(False)

        self.labelRigName = QLabel("Rig is not responding")
        self.rigSelectGroupBox = QGroupBox("Rig select:")
        self.radioBtnTRX1 = QRadioButton("Rig 1")
        self.radioBtnTRX1.setChecked(True)
        self.radioBtnTRX1.toggled.connect(self.refreshRigInformation)
        self.radioBtnTRX2 = QRadioButton("Rig 2")
        self.radioBtnTRX2.toggled.connect(self.refreshRigInformation)

        hboxRigSelect = QHBoxLayout()
        hboxRigSelect.addWidget(self.radioBtnTRX1)
        hboxRigSelect.addWidget(self.radioBtnTRX2)
        self.rigSelectGroupBox.setLayout(hboxRigSelect)

        self.lcdTrxFrequency = QLCDNumber(10)
        self.lcdTrxFrequency.display('00.000.00')
        self.lcdTrxFrequency.setPalette(self.blackColorPalette)
        self.lcdTrxFrequency.setMinimumHeight(50)
        self.lcdTrxFrequency.setMaximumHeight(50)
        self.lcdTrxFrequency.setMaximumWidth(275)

        self.vboxMainLayout = QVBoxLayout()
        self.vboxMainLayout.addWidget(self.rigSelectGroupBox)
        self.vboxMainLayout.addWidget(self.lcdTrxFrequency)
        self.vboxMainLayout.addWidget(self.labelRigName)

        grid = QGridLayout()
        grid.setSpacing(3)
        grid.addWidget(self.rigSelectGroupBox, 1, 0)
        grid.addWidget(self.lcdTrxFrequency, 1, 1, 1, 5)

        self.labelRigModeLSB = QLabel('LSB')
        self.labelRigModeLSB.setFont(self.boldFont)
        self.labelRigModeLSB.setEnabled(False)

        self.labelRigModeUSB = QLabel('USB')
        self.labelRigModeUSB.setFont(self.boldFont)
        self.labelRigModeUSB.setEnabled(False)

        self.btnOmniRigUSB = QPushButton("USB")
        self.btnOmniRigUSB.clicked.connect(self.btnOmniUSBClick)

        self.btnOmniRigLSB = QPushButton("LSB")
        self.btnOmniRigLSB.clicked.connect(self.btnOmniLSBClick)

        hboxRigModeSetup = QHBoxLayout()
        hboxRigModeSetup.addWidget(self.labelRigModeLSB)
        hboxRigModeSetup.addWidget(self.labelRigModeUSB)
        hboxRigModeSetup.addWidget(self.btnOmniRigLSB)
        hboxRigModeSetup.addWidget(self.btnOmniRigUSB)

        grid2 = QGridLayout()
        grid2.setSpacing(3)
        grid2.addWidget(self.labelRigName, 1, 0)
        grid2.addLayout(hboxRigModeSetup, 1, 1)

        self.vboxMainLayout = QVBoxLayout()
        self.vboxMainLayout.addLayout(grid)
        self.vboxMainLayout.addLayout(grid2)

    def setOmnirigObject(self, omnirigObject):
        self.omnirigObject = omnirigObject

    def btnOmniLSBClick(self):
        if self.omnirigObject is not None:
            if self.radioBtnTRX1.isChecked():
                self.omnirigObject.Rig1.Mode = '67108864'
            else:
                self.omnirigObject.Rig2.Mode = '67108864'

    def btnOmniUSBClick(self):
        if self.omnirigObject is not None:
            if self.radioBtnTRX1.isChecked():
                self.omnirigObject.Rig1.Mode = '33554432'
            else:
                self.omnirigObject.Rig2.Mode = '33554432'

    def setDisplayFreq(self, txtFreq):
        self.lcdTrxFrequency.display(txtFreq)

    def setOmniRigErrorText(self, msgText):
        self.labelRigName.setText(msgText)
        self.labelRigName.setPalette(self.redColorPalette)

    def setRigStatus(self, rigType):
        self.labelRigName.setText(rigType)
        self.labelRigName.setPalette(self.blackColorPalette)

    def getRigsInformation(self):
        return self.omniRigInfo

    def disableControls(self):
        self.radioBtnTRX1.setEnabled(False)
        self.radioBtnTRX2.setEnabled(False)

    def refreshRigInformation(self):
        rignum = '2'
        if self.radioBtnTRX1.isChecked():
            rignum = '1'
        if len(self.omniRigInfo) > 1:
            self.setDisplayFreq(self.addDotsToFreq(self.omniRigInfo[rignum].getRigFreq()))
            self.setRigStatus(self.omniRigInfo[rignum].getRigType() + ": " + self.omniRigInfo[rignum].getRigStatus())

        if self.omniRigInfo[rignum].getRigMode() == 'LSB':
            self.labelRigModeUSB.setEnabled(False)
            self.labelRigModeLSB.setEnabled(True)
        else:
            self.labelRigModeUSB.setEnabled(True)
            self.labelRigModeLSB.setEnabled(False)

    def setRigInformation(self, omniRigInfo):
        self.omniRigInfo = omniRigInfo
        self.refreshRigInformation()

    def addDotsToFreq(self, freqvalue):
        freqTxt = str(freqvalue)
        if len(freqTxt) < 6:
            freqTxt = '00000000'
        firstPart = freqTxt[:-6]
        if len(freqTxt) == 8:
            mainPart = freqTxt[:7]
            middlePart = mainPart[2:5]
            lastPart = mainPart[5:]
        else:
            mainPart = freqTxt[:6]
            middlePart = mainPart[1:4]
            lastPart = mainPart[4:]

        return firstPart+"."+middlePart+"."+lastPart

    def getGUI(self):
        return self.vboxMainLayout

