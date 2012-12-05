import pyaudio
import threading

import storage
import identifier
import Queue
import time

class ProcessData(threading.Thread):
    def __init__(self):
        self.queue = Queue.Queue()
        self.output = None
        self.abandoned = False
        threading.Thread.__init__(self)
        self.daemon = True

    def push_data(self, time, data):
        self.queue.put((time, data), False)

    def abandon(self):
        self.abandoned = True

    def run(self):
        self.data = storage.HashStore()
        chunk_chains = []
        while not self.abandoned or not self.queue.empty():
            print self.queue.qsize()
            t, data = self.queue.get()

            c = identifier.AudioChunk.from_bytes(t, data)

            # Look up any chunks we have in storage by that hash.
            chunks = self.data.get_chunks(c.hash())
            if chunks is not None:

                # Iterate over each chunk we got that matches our hash.
                # For each of those chunks, compare against our 'chunk chains'.
                # If it's both the same song and the time offset matches, update that
                # 'chain' with its new length and offset information.
                # Note: this algorithm is O(n^2).
                # I think it could be reduced to at least O(n log n) without much work, but I'm lazy.
                for new in chunks:
                    handled = False
                    for chain in chunk_chains:
                        if chain[0] != new.song_id:
                            continue
                        if abs((t - chain[1]) - (new.time - chain[2])) < 0.1:
                            chain[1] = t
                            chain[2] = new.time
                            chain[3] += 1

                            handled = True
                            break

                    # If we didn't manage to add this to a chain, create a new entry in the list.
                    if not handled:
                        chunk_chains.append([new.song_id, t, new.time, 1])
            time.sleep(0)       
            for chain in chunk_chains:
                # If we have a chain with over twenty matches, call it a win and bail out.
                if chain[3] >= 20:
                    print "song %d" % chain[0]
                    song = self.data.get_song(chain[0])
                    self.output = (song, chain[2])
                    return

def identify_from_mic():
    p = pyaudio.PyAudio()
    # This is the same set of parameters we used (or, at least, assume) for decoding audio.
    # These must match for sane output.
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=4096)

    time = 0.0

    # List of chunk_chains, given as [song_id, last_offset, song_time, chain_length]
    # Each entry represents a chain of matching points we've found from our incoming mic
    # data. The longer the chain, the more convincing the match/.

    worker = ProcessData()
    worker.start()
    while time < 30:
        data = stream.read(4096)
        worker.push_data(time, data)
        time += (4096/44100.0)

        if worker.output is not None:
            return worker.output

    # Wait for our worker to catch up if we've bailed out
    worker.abandon()
    worker.join()
    if worker.output is not None:
        return worker.output

    return None, None
