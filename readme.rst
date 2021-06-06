Filey
=====

Flexible functions and handy handles for your favourite filey things.

\````python # central_nervous_system.py import os, random

from filey import Address, Directory, File, Library, ffplay, convert

this = **file** here = os.path.dirname(**file**) pwd = Address(here).obj

print(here == str(pwd)) print(isinstance(pwd, Directory))

def cd(path): global pwd if isinstance(path, str): os.chdir(path)
pwd.path = path elif isinstance(path, Directory): path.enter() pwd.path
= path.path else: raise ValueError

user = Directory(ΓÇÿ~ΓÇÖ) music = user / ΓÇ£musicΓÇ¥ artist1 =
music[ΓÇ£Collection/Alix PerezΓÇ¥] artist2 =
music.items.collection[ΓÇ£dBridgeΓÇ¥] # items can be used to access contents
whose names are legal in python album1 = artist1[ΓÇ£1984ΓÇ¥] # raises an
OSError if it cannot be found album2 = music[ΓÇ£collection/dBridge/the
gemini principleΓÇ¥] print(album1.sameas(album2)) # False track1 =
album1[ΓÇÿ05 portraits of the unknownΓÇÖ] # Metadata print(music.mimes) #
(ΓÇÿaudio/mpegΓÇÖ, ΓÇÿaudio/x-wavΓÇÖ, ΓÇÿimage/jpegΓÇÖ, ΓÇÿapplication/x-sqlite3ΓÇÖ)
print(music.kinds) # (ΓÇÿmpegΓÇÖ, ΓÇÿx-wavΓÇÖ, ΓÇÿjpegΓÇÖ, ΓÇÿx-sqlite3ΓÇÖ)
print(music.exts) # (ΓÇÿ.mp3ΓÇÖ, ΓÇÿ.wavΓÇÖ, ΓÇÿ.jpgΓÇÖ, ΓÇÿ.iniΓÇÖ, ΓÇÿ.fplΓÇÖ, ΓÇÿ.itdbΓÇÖ,
ΓÇÿ.itlΓÇÖ, ΓÇÿ.plistΓÇÖ)

Searching and Libraries
=======================

lib = Library(album1, album2, artist1, artist2) playlist =
ΓÇ£*ΓÇ£.join(lib(ΓÇÖΓÇÿ, exts=ΓÇÖAac Midi Mp3 M4a Ogg Flac Wav AmrΓÇÖ)) # search
library for any path-strings regex-matching (non-regex enabled by
default) the empty string. Directories are also searchable via **call**
ffplay(playlist, loop=False, randomize=True, hide=True,
fullscreen=False) # media playback via FFMPEG \``\`
