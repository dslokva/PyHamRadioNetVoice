__author__ = '@sldmk'

import sys
import opuslib
import pyaudio
import traceback
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

rawdatalen = 0
opusdatalen = 0

class OpusCodec():
    def __init__(self, *args, **kwargs):
        self.decoder = opus_decoder.create_state(rate, channels)
        self.encoder = opus_encoder.create_state(rate, channels, opuslib.APPLICATION_VOIP)

        opus_encoder.encoder_ctl(self.encoder, ctl.set_bandwidth, opuslib.constants.BANDWIDTH_FULLBAND)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_signal, opuslib.constants.SIGNAL_VOICE)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_bitrate, 24000)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_inband_fec, 1)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_packet_loss_perc, 10)
        # opus_encoder.encoder_ctl(self.encoder, ctl.set_vbr, 0)

    def encode(self, data):
        out = opus_encoder.encode(self.encoder, data, opus_frame_size, len(data))
        return out

    def decode(self, data):
        out = opus_decoder.decode(self.decoder, data, len(data), opus_frame_size, False, channels)
        return out


class AudioRecorder():
    def __init__(self):
        self.audioIn = pyaudio.PyAudio()
        self.audioOut = pyaudio.PyAudio()
        self.info = self.audioIn.get_host_api_info_by_index(0)
        self.numdevices = self.info.get('deviceCount')
        self.recordingIsActive = False

    def getAudioOutputDevices(self):
        devices = {}
        for i in range(0, self.numdevices):
            devOut = self.audioIn.get_device_info_by_host_api_device_index(0, i)
            if (devOut.get('maxOutputChannels')) > 0:
                d = {devOut.get('index') : devOut.get('name')}
                devices.update(d)
        return devices

    def getAudioInputDevices(self):
        devices = {}
        for i in range(0, self.numdevices):
            devIn = self.audioIn.get_device_info_by_host_api_device_index(0, i)
            if (devIn.get('maxInputChannels')) > 0:
                d = {devIn.get('index') : devIn.get('name')}
                devices.update(d)
        return devices

    def getDefaultAudioInDeviceIndex(self):
        return self.audioIn.get_default_input_device_info()["index"]

    def getDefaultAudioOutDeviceIndex(self):
        return self.audioOut.get_default_output_device_info()["index"]

    def startRec(self):
        self.recordingIsActive = True
        recThread = threading.Thread(target=self.recordingThread, args=())
        recThread.start()

    def stopRec(self):
        self.recordingIsActive = False

    def recordingThread(self):
        stream = self.audioIn.open(format=pyaudio.paInt16, channels=channels,
                                   rate=rate, input_device_index=1, input=True, output=False,
                                   frames_per_buffer=frames_per_buffer)

        streamout = self.audioOut.open(format=pyaudio.paInt16, channels=channels,
                                       rate=rate, input=False, output=True,
                                       output_device_index=self.audioOut.get_default_output_device_info()["index"],
                                       frames_per_buffer=frames_per_buffer)

        codec = OpusCodec()

        while self.recordingIsActive:
            data = stream.read(frames_per_buffer, exception_on_overflow=False)

            opusencoded_data = codec.encode(data)
            opusdecoded_data = codec.decode(opusencoded_data)

            streamout.write(opusdecoded_data)
            # streamout.write(data)

            print("WAW_ORIG: ", len(data),
                  "OPUS_ENCODE: ", len(opusencoded_data),
                  "OPUS_DECODE: ", len(opusdecoded_data))

        if not self.recordingIsActive:
            stream.stop_stream()
            stream.close()
            streamout.stop_stream()
            streamout.close()
            # self.audioIn.terminate()
            # self.audioOut.terminate()

if __name__ == '__main__':
    audiorec = AudioRecorder()
    audiorec.startRec()
