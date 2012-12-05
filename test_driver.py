#!/usr/bin/env python

import storage
import guess
import os

def test_directory(d):
    song_list = [d + '/' + x for x in os.listdir(d)]

    for filename in song_list:
        storage.store_file(filename)
        print "Stored %s (%d unique samples)" % (filename, len(storage.HashTable))

def main():
    audio_dir = raw_input("Enter audio directory: ")
    test_directory(audio_dir)

    while True:
        inp = raw_input("Press return to start listening. Type 'quit' when you're bored.")
        if inp == 'quit':
            break

        song, time = guess.identify_from_mic()
        if song is None:
            print "Sorry, no idea."
        else:
            print "Guessing..."
            print "'%s' by '%s'" % (song.track_name, song.artist)
            minutes = time // 60
            seconds = time % 60
            print "%d:%d into song" % (minutes, seconds)
            print ""

if __name__ == '__main__':
    main()
