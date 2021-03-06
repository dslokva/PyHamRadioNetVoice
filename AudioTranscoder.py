__author__ = '@sldmk'

import numpy
from OPUSCodecImpl import OpusCodec
import pyaudio
from pyaudio import Stream
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

frames_per_buffer = 1920
# frames_per_buffer = 3840
channels = 1
rate = 48000
opus_frame_size = 1920
# opus_frame_size = 3840

class AudioTranscoder:
    def __init__(self, codecBitrate):
        self.audioIn = pyaudio.PyAudio()
        self.audioOut = pyaudio.PyAudio()
        self.info = self.audioIn.get_host_api_info_by_index(0)
        self.numdevices = self.info.get('deviceCount')
        self.codecBitrate = codecBitrate
        self.isRecordingActive = False
        self.rawBytesCount = 0
        self.opusBytesCount = 0
        self.volume = 100
        self.dataLst = []

        self.UDPclients = {}

        # Initialize streams
        self.streamIn = Stream(self, rate=rate, channels=channels, format=pyaudio.paInt16, input=True, output=False)
        self.streamIn.stop_stream()
        self.streamOut = Stream(self, rate=rate, channels=channels, format=pyaudio.paInt16, input=False, output=True)
        self.streamOut.stop_stream()

        self.opusencoded_data = b'\00'

    def setBitrate(self, bitrate):
        self.codecBitrate = bitrate

    def getBitrate(self):
        return self.codecBitrate

    def getAudioOutputDevices(self):
        devices = {}
        for i in range(0, self.numdevices):
            devOut = self.audioOut.get_device_info_by_host_api_device_index(0, i)
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
        threading.Thread(target=self.transcodingThread, args=(idxDevIn, idxDevOut)).start()

    def stopRec(self):
        self.isRecordingActive = False
        self.rawBytesCount = 0
        self.opusBytesCount = 0
        self.removeAllUDPClients()

    def getDataLst(self):
        return self.dataLst

    def clearDataLst(self):
        self.dataLst = []

    def set_audio_volume(self, datalist, volume):
        sound_level = (volume / 100.)
        chunk = numpy.frombuffer(datalist, numpy.int16)
        chunk = chunk * sound_level
        return chunk.astype(numpy.int16).tostring()

    def transcodingThread(self, idxDevIn, idxDevOut):
        self.streamIn = self.audioIn.open(format=pyaudio.paInt16, channels=channels,
                                          rate=rate, input_device_index=idxDevIn, input=True, output=False,
                                          frames_per_buffer=frames_per_buffer)
        if idxDevOut > -1:
            self.streamOut = self.audioOut.open(format=pyaudio.paInt16, channels=channels,
                                                rate=rate, input=False, output=True,
                                                output_device_index=idxDevOut,
                                                frames_per_buffer=frames_per_buffer)

        codec = OpusCodec(channels=channels, rate=rate, frame_size=opus_frame_size, bitrate=self.codecBitrate)

        while self.isRecordingActive:
            data = self.streamIn.read(frames_per_buffer, exception_on_overflow=False)
            #increase volume if needed, may cause some echo effect on high level volume
            data = self.set_audio_volume(data, self.volume)

            self.opusencoded_data = codec.encode(data)
            if len(self.UDPclients) > 0:
                threading.Thread(target=self.udpStreamToClients, args=(self.opusencoded_data,)).start()

            if idxDevOut > -1:
                opusdecoded_data = codec.decode(self.opusencoded_data)
                self.streamOut.write(opusdecoded_data)

        if not self.isRecordingActive:
            self.streamIn.stop_stream()
            self.streamIn.close()

            if self.streamOut is not None:
                self.streamOut.stop_stream()
                if self.streamOut.is_active():
                    self.streamOut.close()
        print("Transcoding thread finished.")

    def addUDPClient(self, clientAddressPort, client_udp_socket):
        self.UDPclients[clientAddressPort] = client_udp_socket

    def removeUDPClient(self, address):
        if len(self.UDPclients) > 0:
            for clientAddressPort, socket in self.UDPclients.items():
                if clientAddressPort.find(address) > -1:
                    del(self.UDPclients[clientAddressPort])
                    socket.close()
                    print("UDP client removed: ", address)
                    break

    def removeAllUDPClients(self):
        if len(self.UDPclients) > 0:
            for clientAddressPort, clientSocket in self.UDPclients.items():
                clientSocket.close()
                print("UDP client removed: ", clientAddressPort)
            self.UDPclients = {}

    def getUDPStreamsCount(self):
        return len(self.UDPclients)

    def udpStreamToClients(self, soundData):
        if len(self.UDPclients) > 0:
            try:
                for clientAddressPort, clientSocket in self.UDPclients.items():
                    address = clientAddressPort.partition(":")[0]
                    port = int(clientAddressPort.partition(":")[2])
                    clientSocket.sendto(soundData, (address, port))
                    self.dataLst.append(len(soundData))
            except:
                pass

    def setVolume(self, volume):
        self.volume = volume
