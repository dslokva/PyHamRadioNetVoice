import opuslib
from opuslib.api import encoder as opus_encoder
from opuslib.api import decoder as opus_decoder
from opuslib.api import ctl

class OpusCodec:

    def __init__(self, channels, rate, frame_size):
        self.decoder = opus_decoder.create_state(rate, channels)
        self.encoder = opus_encoder.create_state(rate, channels, opuslib.APPLICATION_VOIP)
        self.channels = channels
        self.rate = rate
        self.frame_size = frame_size

        opus_encoder.encoder_ctl(self.encoder, ctl.set_bandwidth, opuslib.constants.BANDWIDTH_FULLBAND)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_signal, opuslib.constants.SIGNAL_VOICE)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_bitrate, 24000)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_inband_fec, 1)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_packet_loss_perc, 10)
        opus_encoder.encoder_ctl(self.encoder, ctl.set_vbr, 1)

    def encode(self, data):
        out = opus_encoder.encode(self.encoder, data, self.frame_size, len(data))
        return out

    def decode(self, data):
        out = opus_decoder.decode(self.decoder, data, len(data), self.frame_size, False, self.channels)
        return out