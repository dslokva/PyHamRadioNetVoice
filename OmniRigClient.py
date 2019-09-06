import threading
import time
import pythoncom
import win32com.client as win32
import win32event

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
            guiQtPanel.setOmniRigErrorText('OmniRig connection error', 1)

        if self.omniRigActive:
            win32.WithEvents(omnirigObject, OmniRigEventsHandler)
            threading.Thread(target=self.watchRigEvents, args=()).start()

    def watchRigEvents(self):
        while True:
            evt = win32event.CreateEvent(None, 0, 0, None)
            rc = win32event.MsgWaitForMultipleObjects((evt,), 0, win32event.INFINITE, win32event.QS_ALLEVENTS)
            if rc == win32event.WAIT_OBJECT_0 + 1:
                pythoncom.PumpWaitingMessages()
            time.sleep(.05)
            # a = input()
            # if a == "s":
            #     omnirig.Rig2.SetSimplexMode('7108500')
            #     omnirig.Rig2.Mode = '67108864' #LSB
            # omnirig.Rig2.Mode = '33554432' #USB
class RigParams:
    def __init__(self):
        self.rigType = ''
        self.rigStatus = ''
        self.rigFreq = ''
        self.rigMode = ''


class OmniRigEventsHandler():
    def __init__(self):
        rigInfo = {
            1 : RigParams,
            2 : RigParams
        }

    def OnStatusChange(self, rignum):
        print("OnStatusChange. Rig#" + str(rignum) + omnirigObject.Rig2.StatusStr)
        self.rig1Status = omnirigObject.Rig1.StatusStr
        self.rig2Status = omnirigObject.Rig2.StatusStr

    def OnParamsChange(self, rignum, params):
        modeText = 'USB'
        if omnirigObject.Rig2.Mode == 67108864:
            modeText = 'LSB'

        print("OnParamsChange. Rig#", rignum)
        guiQtPanel.setDisplayFreq(self.addDotsToFreq(omnirigObject.Rig2.Freq))
        guiQtPanel.setRigName(omnirigObject.Rig2.RigType)

    def OnVisibleChange(self):
        print("OnVisibleChange")

    def addDotsToFreq(self, freqvalue):
        freqTxt = str(freqvalue)
        return '111'