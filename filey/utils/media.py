__all__ = 'commons ffplay delevel convert sortbysize'.split()

from typing import Sequence, Iterable
import os, time, re, subprocess, sys

import filetype as ft

from .debug import show


defaultScriptDirectory = r'e:\projects\monties'
commons = {
    """
    Hopefully such hacks as these are now obsolete
    """
    'music': os.path.join(os.path.expanduser('~'), 'music', 'collection'),
    'images': os.path.join(os.path.expanduser('~'), 'pictures'),
    'pictures': os.path.join(os.path.expanduser('~'), 'pictures'),
    'pics': os.path.join(os.path.expanduser('~'), 'pictures'),
    'videos': os.path.join(os.path.expanduser('~'), 'videos'),
    'ytdls': {
        'music': {
            'singles': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'music', 'singles'),
            'mixes': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'music', 'mixes'),
            'albums': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'music', 'album'),
        },
        'graff': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'graff'),
        'bullshit': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'bullshitters'),
        'bull': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'bullshitters'),
        'code': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'cscode'),
        'cs': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'cscode'),
        'maths': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'maths'),
        'math': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'maths'),
        'movies': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'movies'),
        'other': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'other'),
        'physics': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'physics'),
        'phys': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'physics'),
        'politics': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'politics'),
        'pol': os.path.join(os.path.expanduser('~'), 'videos', 'ytdls', 'politics'),
    },
    'documents': os.path.join(os.path.expanduser('~'), 'documents'),
    'docs': os.path.join(os.path.expanduser('~'), 'documents'),
    'downloads': os.path.join(os.path.expanduser('~'), 'downloads'),
    'desktop': os.path.join(os.path.expanduser('~'), 'desktop'),
    'books': os.path.join(os.path.expanduser('~'), 'documents', 'bookes'),
    'monties': os.path.join(defaultScriptDirectory, str(time.localtime()[0])),
    'scripts': defaultScriptDirectory,
    'demos': os.path.join(defaultScriptDirectory, 'demos'),
    'site': os.path.join(sys.exec_prefix, 'lib', 'site-packages'),
    'home': os.path.expanduser('~'),
    'user': os.path.expanduser('~'),
    'root': os.path.expanduser('~'),
    '~': os.path.expanduser('~'),
}
os.makedirs(commons['monties'], exist_ok=True)


def ffplay(files:Sequence[str], hide:bool=True, fullscreen:bool=True, loop:bool=True, quiet:bool=True, randomize:bool=True, silent:bool=False) -> None:
    """
    Play a collection of files using ffmpeg's ffplay cli
    Dependencies: FFMPEG,subprocess,os
    In: files,fullscreen=True,quiet=True
    Out: None
    
    If entering files as a string, separate each path by an asterisk (*), othewise feel free to use any iterator
    -loop {f"-loop {loop}" if loop else ""}
    """
    namext = lambda file: os.path.split(file)[1]
    nome = lambda file: os.path.splitext(namext(file))[0]
    ext = lambda file: os.path.splitext(file)[1]
    isvid = lambda file: ft.match(file) in ft.video_matchers
    vidtitle = lambda vid: '-'.join(i.strip() for i in vid.split('-')[:-1])
    albumtrack = lambda file: bool(re.search(f'\d+\s.+{ext(file)}', file, re.I))
    attitle = lambda file: ' '.join(i.strip() for i in nome(file).split(' ')[1:])
    aov = lambda file: albumtrack(file) or isvid(file)
    title = lambda file: ''.join(i for i in os.path.splitext(namext(file)[1])[0] if i not in '0123456789').strip()
    windowtitle = lambda file: [namext(file),[attitle(file),vidtitle(file)][isvid(file)]][aov(file)]
    play = lambda file: subprocess.run(f'ffplay {("", "-nodisp")[hide]} -window_title "{windowtitle(file)}" -autoexit {"-fs" if fullscreen else ""} {"-v error" if quiet else ""} "{file}"')
    files = files.split('*') if isinstance(files,str) else files
    if loop:
        while (1 if loop==True else loop+1):
            files = shuffle(files) if randomize else files
            for i,f in enumerate(files, 1):
                if os.path.isdir(f):
                    fls = [os.path.join(f, i) for i in gather(f, names=False)]
                    for j,file in enumerate(fls, 1):
                        name = os.path.split(file)[1]
                        print(f'{j} of {len(fls)}:\t{name}') if not silent else None
                        ffplay(file, hide, fullscreen, False, quiet, randomize, True)
                else:
                    folder,name = os.path.split(f)
                    print(f'{i} of {len(files)}:\t{name}') if not silent else None
                    play(f)
            loop -= 1
    else:
        files = shuffle(files) if randomize else files
        for i, f in enumerate(files, 1):
            if os.path.isdir(f):
                fls = [os.path.join(f, i) for i in gather(f, names=False)]
                for j, file in enumerate(fls, 1):
                    name = os.path.split(file)[1]
                    print(f'{j} of {len(fls)}:\t{name}') if not silent else None
                    ffplay(file, hide, fullscreen, False, quiet, randomize, True)
            else:
                print(f'{i} of {len(files)}:\t{title(f)}') if not silent else None
                play(f)


def delevel(path:str, steps:int=1) -> str:
    """
    This will climb the given path tree by the given number of steps.
    No matter how large the number of steps, it will stop as soon as it reaches the root.
    Probably needs revision for paths on systems which hide the root drive.
    example
        >>> for i in range(4):print(delevel(r'c:/users/admin',i))
        c:/users/admin
        c:/users
        c:/
        c:/
    dependencies: os.sep
    """
    while steps and (len(path.split(os.sep))-1):
        path = os.sep.join((path.split(os.sep)[:-1]))
        steps -= 1
    return path if not path.endswith(':') else path+os.sep


def convert(file:str, format:str='.wav', bitRate:int=450, delete:bool=False, options:str=''):
    """
    Convert an audio file
    Dependencies: m3ta.nameUpdater, send2trash, ffmpeg, subprocess, os
    In: file,format='.wav',bitRate=450,delete=False,options=''
    Outs: None
    """
    trash = tryimport('send2trash','send2trash','remove','os')
    os.chdir(os.path.split(file)[0])
    
    _title = lambda file: file.split(os.sep)[-1].split('.')[0]
    _new = lambda file,format: nameUpdater(_title(file)+format)
    _name = lambda file: file.split(os.sep)[-1]
    format = '.' + format if '.' != format[0] else format
    
    name = _title(file)
    new = _new(file,format)
    cmd = f'ffmpeg -y -i "{file}" -ab {bitRate*1000} "{new}"' if bitRate != 0 else f'ffmpeg {options} -y -i "{file}" "{new}"'
    announcement = f"Converting:\n\t{file} --> {new}\n\t{cmd=}"
    print(announcement)
    subprocess.run(cmd)
    print('Conversion is complete')
    if delete:
        trash(file)
        print(f'Deletion is complete\n\t{new}\n\n\n')
    return new
    

def sortbysize(files:Iterable[str]=None) -> list:
    """
    Sort a collection of file paths by the size of the corresponding files (largest to smallest)
    Dependencies: os
    In: iterableCollection
    Out: list
    """
    files = [os.getcwd(), list(files)][bool(files)]
    size = lambda file: os.stat(file).st_size
    out = []
    while len(files)>0:
        sizes = set(size(file) for file in files)
        for file in files:
            if size(file) == max(sizes):
                out.append(file)
                files.remove(file)
    return out


if __name__ == '__main__':
    mock = 'drive: users user place subplace file.extension.secondextension'.split()
    # mock = 'drive: users user place subplace readme'.split()
    testPaths = [
        ''.join(mock),
        os.path.join(*mock),
        os.path.join(*mock[:4])+'/'+'/'.join(mock[4:]),
        os.path.join(*mock[3:4])+'/'+'/'.join(mock[4:]),
        os.path.join(*mock[:-1]),
        '/'.join(mock[:-1]),
        mock[-1]
    ]
    show(testPaths)
    # show(zip(map(type,map(lambda x: Address(x).obj, testPaths)),testPaths))
    # show(zip(testPaths,map(normalize,testPaths)))
    # show(zip(testPaths,map(hasdirs,testPaths)))
    # show(zip(testPaths,map(likeFile,testPaths)))