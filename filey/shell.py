# __all__ = "discard unarchive create_enter audio_or_video NameSpacer namespacer isempty move send2trash ffplay trim move_file delevel convert cat".split()
__all__ = "mcd mv move_file rm ffplay convert cat".split()

from itertools import filterfalse
from typing import Iterable, Iterator
from warnings import warn
import os, subprocess, sys, time

from send2trash import send2trash
from sl4ng import shuffle, flat
import filetype as ft, audio_metadata as am, pyperclip as pc


def delevel(path: str, steps: int = 1) -> str:
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
    path = os.path.normpath(path)
    while steps and (len(path.split(os.sep)) - 1):
        path = os.sep.join((path.split(os.sep)[:-1]))
        steps -= 1
    return path if not path.endswith(':') else path + os.sep


class NameSpacer:
    """
    Create an incrementation of a path if it already exists on the local system

    params
        format
            a formattable string amenable to both "name" and "index" key words

    examples
        >>> my_path = "c:/users"
        >>> NameSpacer()(my_path)
        c:/users_2
        >>> NameSpacer("{name} ({index})")(my_path)
        c:/users (2)
    """

    def __init__(self, format: str = "_{index}"):
        self.format = format

    def __call__(self, path: str, index: int = 2) -> str:
        if not os.path.exists(path):
            return path
        if os.path.exists(new := self.new(path, index)):
            return self(path, index + 1)
        return new

    def new(self, path: str, index: int) -> str:
        weirdos = ".tar".split()
        name, ext = os.path.splitext(path)
        while any(name.endswith(weirdo := w) for w in weirdos):
            if name != (name := name.removesuffix(weirdo)):
                ext = weirdo + ext
        return name + self.format.format(index=index) + ext


namespacer = NameSpacer()


def trim(path: str, edge: str = os.sep) -> str:
    """
    Remove trailing/leading separators (or edges) from a path string
    """
    out = path[:]
    if sys.platform == 'win32':
        while any(out.startswith(x) for x in (edge, ' ')):
            out = out[1:]
    while any(out.endswith(x) for x in (edge, ' ')):
        out = out[:-1]
    return out


def cat(
    path: str, text: bool = True, lines: bool = False, copy: bool = False
) -> str | bytes | list[str | bytes]:
    """
    Extract the text or bytes, if the keyword is set to false, from a file
    ::text::
        text or bytes?
    ::lines::
        split text by line or return raw?
    """
    if os.path.isfile(path):
        mode = "rb r".split()[text]
        with open(path, mode) as f:
            content = f.readlines() if lines else f.read()
            pc.copy(content) if copy else None
            return content


def create_enter(
    *args: [str, Iterable[str]],
    go_back: bool = False,
    recursive: bool = True,
    overwrite: bool = True,
    exist_ok: bool = True,
) -> str:
    """
    recursively create and enter directories.
    params:
        go_back
            if set to True, the process will return to the starting directory
        recursive
            if set to False, all directories will be created in the starting directory
        overwrite
            if a directory "dir_n" exists, "dir_n+1" will be created, unless set to False
        exist_ok
            passed to the os.makedirs call. If set to False, and overwrite is True, and collision occurs, an exception will be raised
    eg
        each of the following calls create the following tree:
            dir-1
                dir0: starting directory
                    dir1
                        dir2
                        dir3
                    dir4
            dir5

        >>> mcd('dir1 dir2 .. dir3 .. .. dir4 .. .. dir5'.split())
        >>> mcd('dir1/dir2 ../dir3 ../../dir4 ../../dir5'.split())
    """
    home = os.getcwd()
    for arg in flat(args):
        arg = namespacer(arg) if arg != '..' and not overwrite else arg
        os.makedirs(arg, exist_ok=exist_ok)
        os.chdir(arg if recursive else home)
    last_stop = home if go_back else os.getcwd()
    os.chdir(last_stop)
    return last_stop


mcd = create_enter


def move(source: str, dest: str, make_dest: bool = False) -> str:
    """
    Move source to dest
    Return path to new version

    Params
        source
            path to original file/folder
        dest
            path to new containing directory.
            This will assume that the directory is on the same disk as os.getcwd()
        make_dest
            create destination if it doesn't already exist
    """
    dest = (os.path.realpath, str)[os.path.isabs(dest)](dest)
    if not os.path.isdir(dest):
        if not make_dest:
            raise ValueError(f"Destination's path doesn't point to a directory")
        os.makedirs(dest, exist_ok=True)
    root, name = os.path.split(source)
    new = os.path.join(dest, name)
    os.rename(source, new)
    return new


mv = move


def move_file(
    file: str, dest: str, make_dest: bool = False, clone: bool = False
) -> str:
    """
    Move a file to a given directory
    This uses iteration to copy the file byte by byte.
        Use filey.operations.move unless you're having some permission issues
    Params
        source
            path to original file/folder
        dest
            path to new containing directory.
            This will assume that the directory is on the same disk as os.getcwd()
        make_dest
            create destination if it doesn't already exist
    """
    if os.path.isdir(source):
        raise ValueError(f"Source path points to a directory")

    dest = (os.path.realpath, str)[os.path.isabs(dest)](dest)
    if not os.path.isdir(dest):
        if not make_dest:
            raise ValueError(f"Destination path doesn't point to a directory")
        else:
            os.makedirs(dest, exist_ok=True)

    root, name = os.path.split(path)
    new = os.path.join(dest, name)

    with open(source, 'rb') as src:
        with open(new, 'wb') as dst:
            dst.write(src.read())
    try:
        None if clone else os.remove(file)
    except PermissionError:
        warn("Could not remove file after copying due to PermissionError", Warning)
    return new


def discard(path: str, recycle: bool = True) -> None:
    """
    Remove an address from the file-system.
    Will fall back to recycle if recycle is False, but a permission error is raised, and vis-versa
    Params
        Path
            address of the file/folder you wish to remove
        recycle
            send to (True -> recycle bin, False -> anihilate)
    """
    fb = (os.remove, send2trash)
    first, backup = fb if not recycle else fb[::-1]
    try:
        first(path)
    except PermissionError:
        backup(path)


rm = discard


def audio_or_video(path: str) -> bool:
    """
    Check if a file is audio or video
    True if audio, False if video, else ValueError
    """
    if ft.video_match(path):
        return False
    elif ft.audio_match(path):
        return True
    raise ValueError("Mime does not compute")


def ffplay(
    files: Iterable[str],
    hide: bool = True,
    fullscreen: bool = True,
    loop: bool = True,
    quiet: bool = True,
    randomize: bool = True,
    silent: bool = False,
) -> None:
    """
    Play a collection of files using ffmpeg's "ffplay" cli
    Files can be passed as a single string of paths separated by asterisks

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
    aov = lambda file: audio_or_video(file)
    title = lambda file: ''.join(
        i for i in os.path.splitext(namext(file)[1])[0] if i not in '0123456789'
    ).strip()
    windowtitle = lambda file: [
        namext(file),
        [attitle(file), vidtitle(file)][isvid(file)],
    ][aov(file)]
    play = lambda file: subprocess.run(
        f'ffplay {("", "-nodisp")[hide]} -window_title "{windowtitle(file)}" -autoexit'
        f' {"-fs" if fullscreen else ""} {"-v error" if quiet else ""} "{file}"'
    )
    files = files.split('*') if isinstance(files, str) else files
    if loop:
        while 1 if loop == True else loop + 1:
            files = shuffle(files) if randomize else files
            for i, f in enumerate(files, 1):
                if os.path.isdir(f):
                    fls = [os.path.join(f, i) for i in gather(f, names=False)]
                    for j, file in enumerate(fls, 1):
                        name = os.path.split(file)[1]
                        print(f'{j} of {len(fls)}:\t{name}') if not silent else None
                        ffplay(file, hide, fullscreen, False, quiet, randomize, True)
                else:
                    folder, name = os.path.split(f)
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


def convert(
    file: str,
    format: str = 'wav',
    bitRate: int = 450,
    delete: bool = False,
    options: str = '',
) -> str:
    """
    Convert an audio file using FFMPEG.
        Verbosity is minimized by default.
    Params
        file
            path to target file
        format
            desired output format
        bitRate
            only applies to lossy formats like ogg and mp3, will be autocorrected by FFMPEG
        delete
            whether or not to keep the file upon completion
        options
            additional options to pass to ffmpeg
    """
    os.chdir(os.path.split(file)[0])

    _title = lambda file: file.split(os.sep)[-1].split('.')[0]
    _new = lambda file, format: namespacer(_title(file) + format)
    _name = lambda file: file.split(os.sep)[-1]
    format = '.' + format if '.' != format[0] else format

    name = _title(file)
    new = _new(file, format)

    cmd = (
        f'ffmpeg -y -i "{file}" -ab {bitRate*1000} "{new}"'
        if bitRate != 0
        else f'ffmpeg {options} -y -i "{file}" "{new}"'
    )
    announcement = f"Converting:\n\t{file} --> {new}\n\t{cmd=}"
    print(announcement)
    subprocess.run(cmd)
    print('Conversion is complete')
    if delete:
        send2trash(file)
        print(f'Deletion is complete\n\t{new}\n\n\n')
    return new


def unarchive(path: str, app: str = 'rar') -> str:
    """
    Extract an archive to a chosen destination, or one generated based on the name of the archive
    App refers to the comandlet you wish to invoke via subprocess.run

    """
    path = os.path.realpath(path)
    route, namext = os.path.split(path)
    name, ext = os.path.splitext(namext)
    dest = namespacer(os.path.join(route, name))

    options = {'tar': '-x -f', 'rar': 'e -or -r', 'winrar': ''}
    cmd = f'{app} {options[app]} "{src}" '

    os.makedirs(dest, exist_ok=True)
    os.chdir(dest)

    subprocess.run(cmd)
    return dest


def isempty(path: str, make: bool = False) -> bool:
    """
    Check if a given file or folder is empty or not with the option to create it if it doesn't exit
    """
    if os.path.isfile(path):
        with open(path, 'rb') as f:
            return not bool(len(tuple(i for i in f)))
    elif os.path.isdir(path):
        return not bool(len(os.listdir(path)))
    elif make:
        if os.path.splitext(path)[-1]:
            x = open(path, 'x')
            x.close()
        else:
            os.makedirs(path, exist_ok=True)
        return True
