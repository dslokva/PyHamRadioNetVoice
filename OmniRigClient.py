import threading
import time
import pythoncom
import win32com.client as win32
import win32event

omnirigObject = win32.gencache.EnsureDispatch('OmniRig.OmniRigX')
global guiQtPanel

class OmniRigClient:
    def __init__(self, guipan):
        global guiQtPanel
        guiQtPanel = guipan

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

class OmniRigEventsHandler():
    def OnStatusChange(self, rignum):
        print("OnStatusChange. Rig#", rignum)
        print(str(rignum) + omnirigObject.Rig2.StatusStr)

    def OnParamsChange(self, rignum, params):
        modeText = 'USB'
        if omnirigObject.Rig2.Mode == 67108864:
            modeText = 'LSB'
        print("OnParamsChange. Rig#", rignum)
        print(omnirigObject.Rig2.RigType, omnirigObject.Rig2.Freq, modeText)
        guiQtPanel.setDisplayFreq(self.addDotsToFreq(omnirigObject.Rig2.Freq))

    def OnVisibleChange(self):
        print("OnVisibleChange")

    def addDotsToFreq(self, freqvalue):
        freqTxt = str(freqvalue)
        return '111'