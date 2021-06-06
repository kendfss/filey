Flexible functions and handy handles for your favourite filey things.

ΓÇ£ΓÇ£ΓÇ£python # central_nervous_system.py import os

from filey import Directory, File, ffplay, convert

this = **file** here = os.path.dirname(**file**) pwd = Directory(here)

here == str(pwd) # True

def cd(path): global pwd os.chdir(path) pwd.path = path

.. raw:: html

   <!-- c = Directory('c:/') -->

.. raw:: html

   <!-- e = Directory('e:/') -->

.. raw:: html

   <!-- f = Directory('f:/') -->

user = Directory(ΓÇÿ~ΓÇÖ) music = user / ΓÇ£musicΓÇ¥ album1 =
music[ΓÇ£collection/Alix Perez/1984ΓÇ¥] # raises an OSError if it cannot be
found album2 = music[ΓÇ£collection/dBridge/the gemini principleΓÇ¥] artist1
= music.items.collection[ΓÇ£venuq/escrowsΓÇ¥] playlist = Library(album1,
album2, artist1) for track in playlist(ΓÇÖΓÇÖ): # search library for any
matches of the empty string. Directories are also searchable via
**call** ffplay(track.path)

ΓÇ£ΓÇ£ΓÇ¥
