
class Encoder(object):
    def encode(self, s):
        return s[::-1]

class Decoder(object):
    def decode(self, s):
        return ''.join(reversed(list(s)))