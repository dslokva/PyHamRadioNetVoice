import pythoncom
import win32com.client as win32
import win32event

class OmniRigEvents:
    def OnStatusChange(self, rignum):
        print("OnStatusChange")
        print(omnirig.Rig2.StatusStr)

    def OnParamsChange(self, rignum, params):
        print("OnParamsChange. Rig#", rignum)
        print(omnirig.Rig2.RigType, omnirig.Rig2.Freq)

    def OnVisibleChange(self):
        print("OnVisibleChange")

if __name__ == '__main__':
    omnirig = win32.gencache.EnsureDispatch('OmniRig.OmniRigX')
    win32.WithEvents(omnirig, OmniRigEvents)

    while True:
        evt = win32event.CreateEvent(None, 0, 0, None)
        rc = win32event.MsgWaitForMultipleObjects((evt,), 0, win32event.INFINITE, win32event.QS_ALLEVENTS)
        if rc == win32event.WAIT_OBJECT_0 + 1:
            pythoncom.PumpWaitingMessages()

        # a = input()
        # if a == "s":
        #     omnirig.Rig2.SetSimplexMode('7108500')
        # omnirig.Rig2.Mode = '67108864' #LSB
        # omnirig.Rig2.Mode = '33554432' #USB

    sys.exit(app.exec_())