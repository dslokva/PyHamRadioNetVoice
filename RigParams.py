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