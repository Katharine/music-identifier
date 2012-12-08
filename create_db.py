#!/usr/bin/env python
import storage
import os
import audiotools

def store_dir(d):
    store = storage.HashStore()
    for root, bar, files in os.walk(d):
        for filename in files:
            filename = root + '/' + filename
            try:
                store.store_file(filename)
                print "Stored %s" % filename
            except audiotools.UnsupportedFile:
                print "Skipping unsupported file %s" % filename
            except Exception, e:
                print e

def main():
    d = raw_input("Enter the path to the music directory: ")
    store_dir(d)
    print "Done."

if __name__ == '__main__':
    main()