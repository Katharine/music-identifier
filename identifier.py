import audiotools
import audiotools.pcmconverter
import numpy
from numpy import fft, fromstring, int16, abs

class Song(object):
    def __init__(self, name, artist, chunks=None):
        self.track_name = name
        self.artist = artist
        self.chunks = chunks

    @classmethod
    def from_file(self, filename):
        stream = audiotools.open(filename)

        # Deal with the metadata
        metadata = stream.get_metadata()
        if metadata is not None:
            track_name = metadata.track_name if metadata.track_name is not None else filename
            artist = metadata.artist_name
        else:
            track_name = filename
            artist = None

        song = self(track_name, artist)

        # Actually get the chunks we need to do anything useful
        pcm = stream.to_pcm()
        mono = audiotools.pcmconverter.Averager(pcm)
        song.chunks_from_stream(mono)
        
        return song

    def chunks_from_stream(self, s):
        self.chunks = []
        time = 0.0
        while True:
            # Read 4096-ish frames (we should probably care about it being actually 4096 except at the end)
            output = s.read(4096)
            if output.frames == 0: # 0 frames means end of file (you'd expect an EOFError or something, but no...)
                return
            b = output.to_bytes(not numpy.little_endian, True) # Get these out as signed integers in whatever endianness numpy expects
            if len(b) > 0:
                c = AudioChunk.from_bytes(time, b)
                if c is not None:
                    self.chunks.append(c)
            time += output.frames / float(s.sample_rate) # Time is the number of frames over our sampling rate. We need to know it.


class AudioChunk(object):
    fuzz = 2

    @classmethod
    def from_bytes(self, time, b):
        numpy_array = fromstring(b, dtype=int16)
        # Fast-fourier transform for frequencies.
        # Absolute value because we don't care for complex numbers.
        frequencies = abs(fft.rfft(numpy_array))
        # Bin into 40-80, 80-120, 120-180, 180-300
        if len(frequencies) < 181:
            return None
        return self(time, [get_max(frequencies,x[0],x[1]) for x in ((40,80), (80,120), (120,180), (180, 300))])

    def __init__(self, time, bins):
        self.time = time
        self.bins = bins

    def hash(self):
        """ Returns a 32-bit int identifying the chunk """
        a, b, c, d = [x[0] for x in self.bins]
        f = self.fuzz
        # We're never going to try and extract the data from this, so we don't care if we're 
        # overwriting things with oversized numbers.
        return (((a - a%f) << 24) | ((b - b%f) << 16) | ((c - c%f) << 8) | (d - d%f)) & 0xffffffff

    def __repr__(self):
        return "AudioChunk(%f, %s)" % (self.time, self.bins)

def get_max(r, a, b):
    """ Returns the maximum value in the form (index, value). """
    return max([(x+a, r[a:b][x]) for x in xrange(len(r[a:b]))], key=lambda x:x[1])
