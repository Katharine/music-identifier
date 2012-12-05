import identifier
import sqlite3
from collections import namedtuple

ChunkHash = namedtuple('ChunkHash', ('time', 'hash', 'song_id'))

class HashStore(object):
    def __init__(self):
        self.conn = sqlite3.connect('music.db')

    def store_file(self, filename):
        s = identifier.Song.from_file(filename)

        # This should involve a database.
        c = self.conn.cursor()
        c.execute("INSERT INTO songs (track_name, artist) VALUES (?, ?)", (s.track_name, s.artist))
        song_id = c.lastrowid
        c.executemany("INSERT INTO song_chunks (time, hash, song_id) VALUES (?, ?, ?)", [(x.time, x.hash(), song_id) for x in s.chunks])
        self.conn.commit()

    # Should also involve a database
    def get_chunks(self, h):
        c = self.conn.cursor()
        chunks = []
        for row in c.execute("SELECT time, hash, song_id FROM song_chunks WHERE hash = ?", (h,)):
            chunks.append(ChunkHash(time=row[0], hash=row[1], song_id=row[2]))
        return chunks

    def get_song(self, i):
        c = self.conn.cursor()
        c.execute("SELECT track_name, artist FROM songs WHERE rowid = ?", (i,))
        data = c.fetchone()
        if data is None:
            return None
        return identifier.Song(data[0], data[1])
