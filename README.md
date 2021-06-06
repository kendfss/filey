# Filey  

Flexible functions and handy handles for your favourite filey things.  

````python
# central_nervous_system.py
import os, random

from filey import Address, Directory, File, Library, ffplay, convert

this = __file__
here = os.path.dirname(__file__)
pwd = Address(here).obj

print(here == str(pwd))
print(isinstance(pwd, Directory))


def cd(path):
    global pwd
    if isinstance(path, str):
        os.chdir(path)
        pwd.path = path
    elif isinstance(path, Directory):
        path.enter()
        pwd.path = path.path
    else:
        raise ValueError



user = Directory('~')
music = user / "music"
artist1 = music["Collection/Alix Perez"] 
artist2 = music.items.collection["dBridge"] # items can be used to access contents whose names are legal in python
album1 = artist1["1984"] # raises an OSError if it cannot be found
album2 = music["collection/dBridge/the gemini principle"] 
print(album1.sameas(album2))
# False
track1 = album1['05 portraits of the unknown']
# Metadata
print(music.mimes)
# ('audio/mpeg', 'audio/x-wav', 'image/jpeg', 'application/x-sqlite3')
print(music.kinds)
# ('mpeg', 'x-wav', 'jpeg', 'x-sqlite3')
print(music.exts)
# ('.mp3', '.wav', '.jpg', '.ini', '.fpl', '.itdb', '.itl', '.plist')


# Searching and Libraries
lib = Library(album1, album2, artist1, artist2)
playlist = "*".join(lib('', exts='Aac Midi Mp3 M4a Ogg Flac Wav Amr')) # search library for any path-strings regex-matching (non-regex enabled by default) the empty string. Directories are also searchable via __call__
ffplay(playlist, loop=False, randomize=True, hide=True, fullscreen=False) # media playback via FFMPEG
```