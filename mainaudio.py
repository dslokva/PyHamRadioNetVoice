import sys
import opuslib
import pyaudio
from opuslib.api import encoder as opus_encoder
from opuslib.api import decoder as opus_decoder
from opuslib.api import ctl

#good
# frames_per_buffer = 960
# channels = 1
# rate = 8000
# opus_frame_size = 960

# frames_per_buffer = 1280
# channels = 1
# rate = 16000
# opus_frame_size = 1280

frames_per_buffer = 1920
channels = 1
rate = 24000
opus_frame_size = 1920

# frames_per_buffer = 3840
# channels = 1
# rate = 48000
# opus_frame_size = 3840


class OpusCodec():
    def __init__(self, *args, **kwargs):
        self.decoder = opus_decoder.create_state(rate, channels)
        self.encoder = opus_encoder.create_state(rate, channels, opuslib.APPLICATION_AUDIO)

        opus_encoder.encoder_ctl(self.encoder, ctl.set_bandwidth, opuslib.constants.BANDWIDTH_FULLBAND)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_signal, opuslib.constants.SIGNAL_MUSIC)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_bitrate, 12000)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_inband_fec, 1)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_packet_loss_perc, 2)
        # opus_encoder.encoder_ctl(self.encoder, ctl.set_vbr, 0)

    def encode(self, data, **kwargs):
        if not 'frame_size' in kwargs:
            kwargs['frame_size'] = opus_frame_size
        out = opus_encoder.encode(self.encoder, data, opus_frame_size, len(data))
        return out

    def decode(self, data, **kwargs):
        if not 'frame_size' in kwargs:
            kwargs['frame_size'] = opus_frame_size
        out = opus_decoder.decode(self.decoder, data, len(data), opus_frame_size, False, channels)
        return out


class AudioRecorder():
    def __init__(self):
        self.audioIn = pyaudio.PyAudio()
        self.audioOut = pyaudio.PyAudio()
        self.info = self.audioIn.get_host_api_info_by_index(0)
        self.numdevices = self.info.get('deviceCount')

    def startRec(self):
        for i in range(0, self.numdevices):
            if (self.audioIn.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ",
                      self.audioIn.get_device_info_by_host_api_device_index(0, i).get('name'))

        stream = self.audioIn.open(format=pyaudio.paInt16,
                                   channels=channels,
                                   rate=rate,
                                   input_device_index=1,
                                   input=True,
                                   output=False,
                                   frames_per_buffer=frames_per_buffer)

        streamout = self.audioOut.open(format=pyaudio.paInt16,
                                       channels=channels,
                                       rate=rate,
                                       input=False,
                                       output=True,
                                       output_device_index=self.audioOut.get_default_output_device_info()["index"],
                                       frames_per_buffer=frames_per_buffer)

        for i in range(sys.maxsize ** 10):
            try:
                codec = OpusCodec()
                data = stream.read(frames_per_buffer, exception_on_overflow=False)

                opusencoded_data = codec.encode(data)
                opusdecoded_data = codec.decode(opusencoded_data)

                streamout.write(opusdecoded_data)
                # streamout.write(data)

                print("WAW_ORIG: ", len(data),
                      "OPUS_ENCODE: ", len(opusencoded_data),
                      "OPUS_DECODE: ", len(opusdecoded_data))


            except KeyboardInterrupt:
                print("[Keyboard interrupt. Exiting.]")
                stream.stop_stream()
                stream.close()
                self.audioIn.terminate()
                self.audioOut.terminate()
                sys.exit(0)


if __name__ == '__main__':
    audiorec = AudioRecorder()
    audiorec.startRec()
