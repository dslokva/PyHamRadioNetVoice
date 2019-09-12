import pythoncom
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QLabel, QGroupBox, QRadioButton, QHBoxLayout, QLCDNumber, QVBoxLayout, QGridLayout, \
    QPushButton
import win32com.client as win32

class OmniRigQTControls:
    def __init__(self, operatingAsClient, sendCommandFunction=None):
        self.operatingAsClient = operatingAsClient
        self.omnirigObject = None
        self.omniRigInfo = {}
        self.sendCommandFunction = sendCommandFunction
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
        hboxRigSelect.addWidget(self.labelRigName)
        hboxRigSelect.addStretch()
        self.rigSelectGroupBox.setLayout(hboxRigSelect)
        self.rigSelectGroupBox.setMaximumWidth(360)

        self.lcdTrxFrequency = QLCDNumber(10)
        self.lcdTrxFrequency.display('00.000.00')
        self.lcdTrxFrequency.setPalette(self.blackColorPalette)
        self.lcdTrxFrequency.setMinimumHeight(50)
        self.lcdTrxFrequency.setMaximumHeight(50)
        self.lcdTrxFrequency.setMaximumWidth(275)
        self.lcdTrxFrequency.setMinimumWidth(275)

        self.labelRigModeLSB = QLabel('LSB')
        self.labelRigModeLSB.setFont(self.boldFont)
        self.labelRigModeLSB.setEnabled(False)

        self.labelRigModeUSB = QLabel('USB')
        self.labelRigModeUSB.setFont(self.boldFont)
        self.labelRigModeUSB.setEnabled(False)

        vboxMiddlePanel = QVBoxLayout()
        vboxMiddlePanel.addWidget(self.labelRigModeLSB)
        vboxMiddlePanel.addWidget(self.labelRigModeUSB)

        hboxMiddlePanel = QHBoxLayout()
        hboxMiddlePanel.addLayout(vboxMiddlePanel)
        hboxMiddlePanel.addStretch()

        self.btnBack500Hz = QPushButton("<--")
        self.btnBack500Hz.setFixedWidth(50)

        self.btnForward500Hz = QPushButton("-->")
        self.btnForward500Hz.setFixedWidth(50)
        self.btnForward500Hz.clicked.connect(self.btnOmniRigPlus500HzClick)

        self.btnOmniRigUSB = QPushButton("USB")
        self.btnOmniRigUSB.clicked.connect(self.btnOmniUSBClick)
        self.btnOmniRigUSB.setFixedWidth(50)

        self.btnOmniRigLSB = QPushButton("LSB")
        self.btnOmniRigLSB.clicked.connect(self.btnOmniLSBClick)
        self.btnOmniRigLSB.setFixedWidth(50)

        hboxRigCATControl = QHBoxLayout()
        hboxRigCATControl.addWidget(self.btnBack500Hz)
        hboxRigCATControl.addWidget(self.btnForward500Hz)
        hboxRigCATControl.addStretch()
        hboxRigCATControl.addWidget(self.btnOmniRigLSB)
        hboxRigCATControl.addWidget(self.btnOmniRigUSB)
        hboxRigCATControl.addStretch(1)

        hboxMainLayout = QHBoxLayout()
        hboxMainLayout.addWidget(self.lcdTrxFrequency)
        hboxMainLayout.addLayout(hboxMiddlePanel)

        self.vboxMainLayout = QVBoxLayout()
        self.vboxMainLayout.addWidget(self.rigSelectGroupBox)
        self.vboxMainLayout.addLayout(hboxMainLayout)
        if self.operatingAsClient is True:
            self.vboxMainLayout.addLayout(hboxRigCATControl)

    def setOmnirigObject(self, omnirigObject):
        self.omnirigObject = omnirigObject

    def btnOmniRigPlus500HzClick(self):
        try:
            self.omnirigObject = win32.Dispatch("OmniRig.OmniRigX")
        except:
            pass
        if self.omnirigObject is not None and self.operatingAsClient is False:
            if self.radioBtnTRX1.isChecked():
                self.omnirigObject.Rig1.SetSimplexMode(str(self.omnirigObject.Rig1.Freq+500))
            else:
                self.omnirigObject.Rig2.SetSimplexMode(str(self.omnirigObject.Rig1.Freq+500))
        if self.operatingAsClient is True and self.sendCommandFunction is not None:
            self.sendCommandFunction('+500=1')

    def btnOmniLSBClick(self):
        try:
            self.omnirigObject = win32.Dispatch("OmniRig.OmniRigX")
        except:
            pass
        if self.omnirigObject is not None and self.operatingAsClient is False:
            if self.radioBtnTRX1.isChecked():
                self.omnirigObject.Rig1.Mode = '67108864'
            else:
                self.omnirigObject.Rig2.Mode = '67108864'
        if self.operatingAsClient is True and self.sendCommandFunction is not None:
            self.sendCommandFunction('setLSB=1')

    def btnOmniUSBClick(self):
        try:
            self.omnirigObject = win32.Dispatch("OmniRig.OmniRigX")
        except:
            pass
        if self.omnirigObject is not None and self.operatingAsClient is False:
            if self.radioBtnTRX1.isChecked():
                self.omnirigObject.Rig1.Mode = '33554432'
            else:
                self.omnirigObject.Rig2.Mode = '33554432'

        if self.operatingAsClient is True and self.sendCommandFunction is not None:
            self.sendCommandFunction('setUSB=1')

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
            self.radioBtnTRX1.setText(self.omniRigInfo['1'].getRigType())
            self.radioBtnTRX2.setText(self.omniRigInfo['2'].getRigType())
            freqTxt = self.omniRigInfo[rignum].getRigFreq()
            self.setDisplayFreq(self.addDotsToFreq(freqTxt))
            self.setRigStatus(self.omniRigInfo[rignum].getRigStatus())

            if freqTxt == 0:
                self.labelRigModeUSB.setEnabled(False)
                self.labelRigModeLSB.setEnabled(False)
            else:
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

