import threading
import time
import pythoncom
import win32com.client as win32
import win32event
from win32com.test.policySemantics import Error

global omnirigObject
global guiQtPanel

class OmniRigClient:
    def __init__(self, guipan):
        global guiQtPanel
        global omnirigObject

        self.omniRigActive = False
        guiQtPanel = guipan
        try:
            omnirigObject = win32.gencache.EnsureDispatch('OmniRig.OmniRigX')
            self.omniRigActive = True
        except:
            guiQtPanel.setOmniRigErrorText('OmniRig connection error')
            guiQtPanel.disableControls()

        if self.omniRigActive:
            win32.WithEvents(omnirigObject, OmniRigEventsHandler)
    #         threading.Thread(target=self.watchRigEvents, args=()).start()
    #
    # def watchRigEvents(self):
    #     pass
    # while self.omniRigActive:
    #     evt = win32event.CreateEvent(None, 0, 0, None)
    #     rc = win32event.MsgWaitForMultipleObjects((evt,), 0, win32event.INFINITE, win32event.QS_ALLEVENTS)
    #     if rc == win32event.WAIT_OBJECT_0 + 1:
    #         pythoncom.PumpWaitingMessages()
    #     time.sleep(.1)
    #     print("OmniRig watch thread terminated")
    #     omnirig.Rig2.SetSimplexMode('7108500')
    #     omnirig.Rig2.Mode = '67108864' #LSB
    #     omnirig.Rig2.Mode = '33554432' #USB

    def setClientActive(self, state):
        self.omniRigActive = state

class RigParams:
    def __init__(self):
        self.rigType = ''
        self.rigStatus = ''
        self.rigFreq = ''
        self.rigMode = ''

    def setRigStatus(self, txt):
        self.rigStatus = txt

    def setRigType(self, txt):
        self.rigType = txt

    def setRigFreq(self, txt):
        self.rigFreq = txt

    def setRigMode(self, txt):
        self.rigMode = txt

    def getRigStatus(self):
        return self.rigStatus

    def getRigType(self):
        return self.rigType

    def getRigFreq(self):
        return self.rigFreq

    def getRigMode(self):
        return self.rigMode

class OmniRigEventsHandler:
    def __init__(self):
        self.omniRigInfo = {
            1: RigParams,
            2: RigParams
        }

        self.rig1ModeText = ''
        self.rig2ModeText = ''
        self.rig1 = RigParams()
        self.rig2 = RigParams()
        self.omniRigInfo[1] = self.rig1
        self.omniRigInfo[2] = self.rig2

    def OnStatusChange(self, rignum):
        print("OnStatusChange. Rig#" + str(rignum))
        self.updateRigTextInfo()

    def OnParamsChange(self, rignum, params):
        self.rig1ModeText = 'USB'
        if omnirigObject.Rig1.Mode == 67108864:
            self.rig1ModeText = 'LSB'

        self.rig2ModeText = 'USB'
        if omnirigObject.Rig2.Mode == 67108864:
            self.rig2ModeText = 'LSB'

        print("OnParamsChange. Rig#", rignum)
        self.updateRigTextInfo()

    def updateRigTextInfo(self):
        self.rig1.setRigStatus(omnirigObject.Rig1.StatusStr)
        self.rig1.setRigFreq(omnirigObject.Rig1.Freq)
        self.rig1.setRigType(omnirigObject.Rig1.RigType)
        self.rig1.setRigMode(self.rig1ModeText)

        self.rig2.setRigStatus(omnirigObject.Rig2.StatusStr)
        self.rig2.setRigFreq(omnirigObject.Rig2.Freq)
        self.rig2.setRigType(omnirigObject.Rig2.RigType)
        self.rig2.setRigMode(self.rig2ModeText)

        guiQtPanel.setRigInformation(self.omniRigInfo)

    def OnVisibleChange(self):
        print("OnVisibleChange")
