__author__ = '@sldmk'


import opuslib
import pyaudio
from pyaudio import Stream
from opuslib.api import encoder as opus_encoder
from opuslib.api import decoder as opus_decoder
from opuslib.api import ctl
import threading

# good
# frames_per_buffer = 960
# channels = 1
# rate = 8000
# opus_frame_size = 960

# frames_per_buffer = 1280
# channels = 1
# rate = 16000
# opus_frame_size = 1280

# frames_per_buffer = 1920
# channels = 1
# rate = 24000
# opus_frame_size = 1920

frames_per_buffer = 3840
channels = 1
rate = 48000
opus_frame_size = 3840

class OpusCodec:
    def __init__(self):
        self.decoder = opus_decoder.create_state(rate, channels)
        self.encoder = opus_encoder.create_state(rate, channels, opuslib.APPLICATION_VOIP)

        opus_encoder.encoder_ctl(self.encoder, ctl.set_bandwidth, opuslib.constants.BANDWIDTH_FULLBAND)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_signal, opuslib.constants.SIGNAL_VOICE)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_bitrate, 24000)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_inband_fec, 1)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_packet_loss_perc, 10)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_vbr, 1)

    def encode(self, data):
        out = opus_encoder.encode(self.encoder, data, opus_frame_size, len(data))
        return out

    def decode(self, data):
        out = opus_decoder.decode(self.decoder, data, len(data), opus_frame_size, False, channels)
        return out

class AudioRecorder:
    def __init__(self):
        self.audioIn = pyaudio.PyAudio()
        self.audioOut = pyaudio.PyAudio()
        self.info = self.audioIn.get_host_api_info_by_index(0)
        self.numdevices = self.info.get('deviceCount')
        self.isRecordingActive = False
        self.rawBytesCount = 0
        self.opusBytesCount = 0

        # Initialize streams
        self.streamIn = Stream(self, rate=rate, channels=channels, format=pyaudio.paInt16, input=True, output=False)
        self.streamIn.stop_stream()
        self.streamOut = Stream(self, rate=rate, channels=channels, format=pyaudio.paInt16, input=False, output=True)
        self.streamOut.stop_stream()

    def getAudioOutputDevices(self):
        devices = {}
        for i in range(0, self.numdevices):
            devOut = self.audioIn.get_device_info_by_host_api_device_index(0, i)
            if (devOut.get('maxOutputChannels')) > 0:
                d = {devOut.get('index'): devOut.get('name')}
                devices.update(d)
        return devices

    def getAudioInputDevices(self):
        devices = {}
        for i in range(0, self.numdevices):
            devIn = self.audioIn.get_device_info_by_host_api_device_index(0, i)
            if (devIn.get('maxInputChannels')) > 0:
                d = {devIn.get('index'): devIn.get('name')}
                devices.update(d)
        return devices

    def getDefaultAudioInDeviceIndex(self):
        return self.audioIn.get_default_input_device_info()["index"]

    def getDefaultAudioOutDeviceIndex(self):
        return self.audioOut.get_default_output_device_info()["index"]

    def startRec(self, idxDevIn, idxDevOut):
        self.isRecordingActive = True
        recThread = threading.Thread(target=self.transcodingThread, args=(idxDevIn, idxDevOut))
        recThread.start()
        threading.Timer(1.0, self.periodicStatsClear).start()

    def stopRec(self):
        self.isRecordingActive = False
        self.rawBytesCount = 0
        self.opusBytesCount = 0

    def updateStats(self, rawBytesCount, opusBytesCount):
        self.rawBytesCount += rawBytesCount
        self.opusBytesCount += opusBytesCount

    def periodicStatsClear(self):
        # print("data stats 1 sec, raw: ", self.rawBytesCount, "opus data: ", self.opusBytesCount)
        self.rawBytesCount = 0
        self.opusBytesCount = 0
        t = threading.Timer(1, self.periodicStatsClear)
        if self.isRecordingActive is True:
            t.start()

    def transcodingThread(self, idxDevIn, idxDevOut):
        self.streamIn = self.audioIn.open(format=pyaudio.paInt16, channels=channels,
                                          rate=rate, input_device_index=idxDevIn, input=True, output=False,
                                          frames_per_buffer=frames_per_buffer)
        if idxDevOut > -1:
            self.streamOut = self.audioOut.open(format=pyaudio.paInt16, channels=channels,
                                                rate=rate, input=False, output=True,
                                                output_device_index=idxDevOut,
                                                frames_per_buffer=frames_per_buffer)
        codec = OpusCodec()

        while self.isRecordingActive:
            data = self.streamIn.read(frames_per_buffer, exception_on_overflow=False)
            opusencoded_data = codec.encode(data)
            opusdecoded_data = codec.decode(opusencoded_data)

            if idxDevOut > -1:
                self.streamOut.write(opusdecoded_data)

            self.updateStats(len(data), len(opusencoded_data))

        if not self.isRecordingActive:
            self.streamIn.stop_stream()
            self.streamIn.close()

            if self.streamOut is not None:
                self.streamOut.stop_stream()
                if self.streamOut.is_active():
                    self.streamOut.close()

# if __name__ == '__main__':
#     audiorec = AudioRecorder()
#     audiorec.startRec()