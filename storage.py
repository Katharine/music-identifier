import identifier

HashTable = {}
Songs = []

def store_file(filename):
    s = identifier.Song.from_file(filename)

    # This should involve a database.
    song_id = len(Songs)
    Songs.append(s)
    for chunk in s.chunks:
        chunk.song_id = song_id # Sad hack to force some sort of back-reference into our Songs table.
        HashTable.setdefault(chunk.hash(), []).append(chunk)

# Should also involve a database
def get_chunks(h):
    return HashTable.get(h)

def get_song(i):
    return Songs[i]


