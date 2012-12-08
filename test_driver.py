#!/usr/bin/env python
import storage
import guess
import os
try:
    import appscript
    has_appscript = True
except:
    has_appscript = False

def main():
    #audio_dir = raw_input("Enter audio directory: ")
    #test_directory(audio_dir)
    if has_appscript:
        itunes = appscript.app('iTunes')
        library = itunes.playlists['Library']


    while True:
        inp = raw_input("Press return to start listening. Type 'quit' when you're bored.")
        if inp == 'quit':
            break
        try:
            song, time = guess.identify_from_mic()
        except IOError:
            print "Mic input failed."
            continue
        if song is None:
            print "Sorry, no idea."
        else:
            print "Guessing..."
            print "'%s' by '%s'" % (song.track_name, song.artist)
            minutes = time // 60
            seconds = time % 60
            print "%d:%d into song" % (minutes, seconds)
            print ""

            if has_appscript:
                itunes_track = library.search(for_=song.track_name + ' ' + song.artist)
                if len(itunes_track) > 0:
                    itunes.play(itunes_track[0], once=True)
                    itunes.player_position.set(time + 0.5)


if __name__ == '__main__':
    main()
