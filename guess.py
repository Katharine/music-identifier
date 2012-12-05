import pyaudio

import storage
import identifier

def identify_from_mic():
    p = pyaudio.PyAudio()
    # This is the same set of parameters we used (or, at least, assume) for decoding audio.
    # These must match for sane output.
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=4096)

    time = 0.0

    # List of chunk_chains, given as [song_id, last_offset, song_time, chain_length]
    # Each entry represents a chain of matching points we've found from our incoming mic
    # data. The longer the chain, the more convincing the match/.
    chunk_chains = []
    while time < 30:
        data = stream.read(4096)
        c = identifier.AudioChunk.from_bytes(time, data)

        # Look up any chunks we have in storage by that hash.
        chunks = storage.get_chunks(c.hash())
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
                    if abs((time - chain[1]) - (new.time - chain[2])) < 0.1:
                        chain[1] = time
                        chain[2] = new.time
                        chain[3] += 1

                        handled = True
                        break

                # If we didn't manage to add this to a chain, create a new entry in the list.
                if not handled:
                    chunk_chains.append([new.song_id, time, new.time, 1])

        for chain in chunk_chains:
            # If we have a chain with over twenty matches, call it a win and bail out.
            if chain[3] >= 20:
                print "song %d" % chain[0]
                song = storage.get_song(chain[0])
                return (song, chain[2])

        time += (4096/44100.0)

    return None
