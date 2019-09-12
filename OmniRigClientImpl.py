import pythoncom
import win32com.client as win32
from RigParams import RigParams

global omnirigObject
global guiQtPanel
global changeEventFunction

class OmniRigClient:
    def __init__(self, guiPanel, changeEventFunc):
        global guiQtPanel
        global omnirigObject
        global changeEventFunction

        self.omniRigActive = False
        guiQtPanel = guiPanel
        changeEventFunction = changeEventFunc
        try:
            pythoncom.CoInitialize()
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

    def getOmniRigObject(self):
        global omnirigObject
        return omnirigObject

    def setClientActive(self, state):
        self.omniRigActive = state

class OmniRigEventsHandler:
    def __init__(self):
        self.omniRigInfo = {
            '1': RigParams,
            '2': RigParams
        }

        self.rig1ModeText = ''
        self.rig2ModeText = ''
        self.rig1 = RigParams()
        self.rig2 = RigParams()
        self.omniRigInfo['1'] = self.rig1
        self.omniRigInfo['2'] = self.rig2

    def OnStatusChange(self, rignum):
        print("OnStatusChange. Rig#" + str(rignum))
        self.updateRigTextInfo()

    def OnParamsChange(self, rignum, params):
        self.getTextMode()
        print("OnParamsChange. Rig#" + str(rignum))
        self.updateRigTextInfo()

    def getTextMode(self):
        self.rig1ModeText = 'USB'
        if omnirigObject.Rig1.Mode == 67108864:
            self.rig1ModeText = 'LSB'
        self.rig2ModeText = 'USB'
        if omnirigObject.Rig2.Mode == 67108864:
            self.rig2ModeText = 'LSB'

    def updateRigTextInfo(self):
        self.getTextMode()
        self.rig1.setRigStatus(omnirigObject.Rig1.StatusStr)
        self.rig1.setRigFreq(omnirigObject.Rig1.Freq)
        self.rig1.setRigType(omnirigObject.Rig1.RigType)
        self.rig1.setRigMode(self.rig1ModeText)

        self.rig2.setRigStatus(omnirigObject.Rig2.StatusStr)
        self.rig2.setRigFreq(omnirigObject.Rig2.Freq)
        self.rig2.setRigType(omnirigObject.Rig2.RigType)
        self.rig2.setRigMode(self.rig2ModeText)

        guiQtPanel.setRigInformation(self.omniRigInfo)
        changeEventFunction()

    def OnVisibleChange(self):
        print("OnVisibleChange")
