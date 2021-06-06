"""
A collection of route objects to help you manage your filey Things and Places elegantly
Exports the following aliases:
    File <-> Thing
    Directory <-> Place
    Path/Address <-> Thing
Thing management wrappers on os.path, shutil, and useful non-standard modules

"Apparent drive" refers to the term before the first os.sep in an object's given path.
    if the given path is relative
        then the ADrive may be ".." or the name of the Thing/Place
    else
        the drive is the name/letter of the disk partition on which the content at the address is stored.
"Apparent Place" similarly refers first term before the last os.sep in an object's given path
    if the given path is relative
        then the ADir may be ".." or the name of the Thing/Place
    else
        the drive is the name/letter of the disk partition on which the content at the address is stored.


TODO
    Add relative path support
    Classes for specific mimes
    A version of @cached_property which checks the date modified before determining whether or not to recompute
    Caches for new directories which include objects to add to them upon creation
    Strict searching
    Caches for pickling (backup simplification)
    Remove Size from repr for Directories. Large ones take too long to initialize
"""
__all__ = 'forbiddens Thing Place Thing Path Address Directory Folder File Library'.split()

from itertools import chain
from typing import Dict, Iterable, Iterator, List, Sequence, TypeAlias
from warnings import warn
import io, os, pathlib, re, sys, shutil

from send2trash import send2trash
from sl4ng import unique, nice_size
from sl4ng import pop, show
import audio_metadata as am, filetype as ft

from . import shell, walking


formats = { # incase mimes fail
    'pics': "bmp png jpg jpeg tiff svg psd".split(),
    'music': "mp3 m4a wav ogg wma flac aiff alac flp live".split(),
    'videos': "mp4 wmv".split(),
    'docs': "doc docx pdf xlsx pptx ppt xls csv".split(),
}
formats['all'] = [*chain.from_iterable(formats.values())]


forbiddens = r'\/:?*<>|"'


_Path:TypeAlias = "Thing"
_Pathstr:TypeAlias = "Thing|str"
_Place:TypeAlias = "Place"
_Placestr:TypeAlias = "Place|str"
_Placefile:TypeAlias = "Place|File"
_File:TypeAlias = "File"
_Filestr:TypeAlias = "File|str"
SYSTEM_PATH:TypeAlias = type(pathlib.Path(__file__))


class MemorySize(int):
    """
    Why should you have to sacrifice utility for readability?
    """
    def __repr__(self):
        return nice_size(self)

class Library:
    """
    Allows categorization for multiple searching and can also be used as a makeshift playlist
    """
    def __init__(self, *paths):
        self.paths = []
        for p in paths:
            if os.path.exists(str(p)):
                self.paths.append(str(p))
        self.index = -1
    def __iter__(self) -> Iterator[str]:
        return self
    def __next__(self) -> str:
        if self.index < len(self.paths) - 1:
            self.index += 1
            return self.paths[self.index]
        self.index = -1
        raise StopIteration
    def __call__(self, terms, **kwargs) -> Iterator[str]:
        """
        Find files under directories in self.paths matching the given terms/criteria
        Any files in self.path will also be yielded if they match

        Params
            Args
                terms:str
                    the terms sought after. 
                    separate by spaces
                    an empty string simply walks the full tree
            Kwargs
                exts:str
                    any file extensions you wish to check for, separate by spaces
                case:bool
                    toggle case sensitivity, assumes True if any terms are upper cased
                negative:bool - kwarg
                    Any files/folders with names or extensions matching the terms and exts will be omitted.
                dirs:int
                    0 -> ignore all directories
                    1 -> directories and files
                    2 -> directories only
                strict:int
                    0 -> match any terms in any order
                    1 -> match all terms in any order (interruptions allowed)
                    2 -> match all terms in any order (no interruptions allowed)
                    3 -> match all terms in given order (interruptions)
                    4 -> match all terms in given order (no interruptions)
                    combinations of the following are not counted as interruptions:
                        [' ', '_', '-']
                    5 -> match termstring as though it was pre-formatted regex
                names:bool
                    True -> only yield results whose names match
                    False -> yield results who match at any level
        """
        for i in self:
            if os.path.isfile(i):
                yield i
            elif os.path.isdir(i):
                yield from walking.search(i, terms, **kwargs)

class Thing:
    """
    Base class for a non-descript path-string. 
    Relative paths are not currently supported
    Methods return self unless otherwise stated
    """
    def __init__(self, path:str):
        self.path = path = os.path.realpath(str(path))
        if not os.path.exists(path):
            warn(f'Warning: Path "{path}" does not exist', Warning)
    def __eq__(self, other:_Pathstr) -> bool:
        if isinstance(other, (str, type(self))):
            return self.sameas(str(other))
        raise NotImplementedError(f"Cannot compare {type(self).__name__} with {type(other).__name__}")
    def __str__(self):
        return self.path
    def __hash__(self):
        """
        Compute the hash of this Thing's path
        """
        return hash(self.path)
    def __repr__(self):
        name = type(self).__name__.split('.')[-1]
        size = f", size={self.size}" if self.isfile or isinstance(self, File) else ''
        real = (f", real={self.exists}", '')[self.exists]
        return f"{name}(name={self.name}, dir={self.up.name}{size}{real})"
    
    def create(self, content:str|bytes|bytearray=None, raw:bool=False, exist_ok:bool=True, mode:int=511) -> _Path:
        """
        Create an entry in the file-system. If the address is not vacant no action will be taken.
        The raw handle only works for Things and enables writing bytes/bytearrays
        """
        if self.exists:
            return self
        elif content or isinstance(self, File):
            os.makedirs(self.up.path, exist_ok=exist_ok)
            if raw:
                if isinstance(content, (bytes, bytearray)):
                    fobj = open(self.path, 'wb')
                else:
                    fobj = open(self.path, 'w')
                fobj.write(content)
                fobj.close()
            else:
                if isinstance(content, str):
                    content = bytes(content, encoding='utf-8')
                else:
                    content = bytes(content)
                with open(self.path, 'wb') as fobj:
                    fobj.write(content)
            self = File(self.path)
        else:
            os.makedirs(self.path, mode=mode, exist_ok=exist_ok)
            self = Place(self.path)
        return self
    @property
    def __short_repr(self) -> str:
        """
        Return check if the Place is at the highest level of the Thing system
        """
        return f"{type(self).__name__}({self.name})"
    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)
    @property
    def isdir(self) -> bool:
        return os.path.isdir(self.path)
    @property
    def isfile(self) -> bool:
        return os.path.isfile(self.path)
    @property
    def obj(self) -> _Path:
        """
        Determine if self.path points to a file or folder and create the corresponding object
        """
        if self.isfile:
            return Thing(self.path)
        elif self.isdir:
            return Place(self.path)
        else:
            return Thing(self.path)
    @property
    def dir(self) -> _Place:
        """
        Return the containing directory
        """
        return Thing(os.path.dirname(self.path)).obj
    up = dir
    @property
    def name(self) -> str:
        """
        Return the name of the referent
        """
        return os.path.split(self.path)[1]
    
    @property
    def ancestors(self) -> tuple:
        """
        Return consecutive ADirs until the ADrive is reached
        """
        level = []
        p = self.path
        while p != delevel(p):
            p = delevel(p)
            level.append(p)
        return tuple(Thing(i).obj for i in level)[::-1]
    @property
    def colleagues(self) -> Iterator:
        """
        Every member of the same Place whose type is the same as the referent
        """
        return (i for i in self.up if isinstance(i, type(self)))
    @property
    def neighbours(self) -> tuple[_File, _Place]:
        """
        Everything in the same Place
        """
        return self.up.content
    @property
    def depth(self) -> int:
        """
        Number of ancestors
        """
        return len(self.ancestors)
    @property
    def top(self) -> str:
        """
        The apparent drive. Will not be helpful if self.path is relative
        """
        return self.ancestors[0]
    @property
    def stat(self) -> os.stat_result:
        """
        return os.stat(self.path) 
        """
        return os.stat(self.path)
    @property
    def ancestry(self) -> str:
        """
        A fancy representation of the tree from the apparent drive up to the given path
        """
        print(f'ancestry({self.name})')
        ancs = list(self.ancestors[1:])
        ancs.append(self.path)
        for i, anc in enumerate(ancs):
            print('\t' + ('', '.' * i)[i > 0] + i * '  ' + [i for i in str(anc).split(os.sep) if i][-1] + '/')
        return self
    @property
    def isempty(self):
        return shell.isempty(self.path, make=False)
    
    def start(self, command:str=None) -> _Path:
        """
        Open the path using the system default or a command of your choice
        """
        pred = isinstance(command, type(None))
        
        arg = (f'{command} "{self.path}"', self.path)[pred]
        fun = (os.system, os.startfile)[pred]
        fun(arg)
        # os.startfile(self.path) if isinstance(command, type(None)) else os.system(f'{self.path} ""')
        return self
    def expose(self):
        """
        Reveal the referent in the system's file explorer (will open the containing Place if the referent is a Thing)
        """
        os.startfile(self.up.path)
        return self
        
    def delevel(self, steps:int=1, path:bool=False) -> str:
        """
        Go up some number of levels in the Thing system
        Params
            steps
                the number of steps to delevel
            path
                return (True -> string, False -> Thing-like object)
        """
        return delevel(self.path, steps) if path else Place(delevel(self.path, steps))
    def touch(self) -> _Path:
        """
        Implements the unix command 'touch', which updates the 'date modified' of the content at the path
        """
        p = self.path
        pathlib.Path(p).touch()
        self = Thing(p).obj
        return self
    def erase(self, recycle:bool=True) -> _Path:
        """
        Send a Thing to the trash, or remove it without recycling.
        """
        shell.discard(self.path, recycle=recycle)
        return self
    def sameas(self, other:_Pathstr) -> bool:
        """
        Check if this Thing's associated data content is equivalent to some other
        """
        if self.exists and os.path.exists(str(other)):
            return os.path.samefile(self.path, str(other))
        else:
            raise OSError("One or both paths point to a non-existent entity")
    def clone(self, folder:str=None, name:str=None, sep:str='_', touch=False) -> _Path:
        """
        Returns a clone of the referent at a given Place-path
        The given path will be created if it doesn't exist
        Will copy in the Thing's original folder if no path is given
        The cwd switch will always copy to the current working Place
        """
        copier = (shutil.copy2, shutil.copytree)[self.isdir]
        if not self.exists:
            raise NotImplementedError(f"Copying is not implemented for inexistant files/directories")
        elif folder:
            new = os.path.join(folder, name if name else self.name)
        else:
            new = self.path
        new = shell.namespacer(new, sep=sep)
        os.makedirs(delevel(new), exist_ok=True)
        copier(self.path, new)
        out = Thing(new).obj
        return out.touch() if touch else out
    def move(self, folder:_Placestr, dodge:bool=False) -> _Path:
        """
        This will clone and delete the underlying file/directory
        addy.move(folder) -> move to the given Place ()
        addy.move(name) -> move to the given path (relative paths will follow from the objects existing path)
        addy.move(folder, name) -> move to the given Place 
        
        :param dodge: 
            enables automatic evasion of file-system collisions
        :param sep: 
            chooses the separator you use between the object's name and numerical affix in your directory's namespace
            **inert if dodge is not True
        :param recycle: 
            enables you to avoid the PermissionError raised by os.remove (if you have send2trash installed)
            ** the PermissionError is due to the object being in use at the time of attempted deletion
       """
        if not self.exists:
            raise OSError(f"{ self.__short_repr} does not exist")
        folder = str(folder)
        if not os.path.exists(folder):
            raise OSError(f"folder={other.__short_repr} does not exist")
        self.path = shell.move(self.path, folder)
        return self
    def rename(self, name:str) -> _Path:
        """
        Change the name of the referent
        This will clone and delete the underlying file/directory
        """
        path = os.path.join(self.dir.path, name)
        os.rename(self.path, path)
        self.path = path
        return self
Address = Path = Thing


class File(Thing):
    """
    Create a new File object for context management and ordinary operations
    """
    def __init__(self, path:str='NewThing'):
        path = os.path.abspath(shell.trim(path))
        if os.path.isdir(path):
            raise ValueError("Given path corresponds to a directory")
        super(type(self), self).__init__(path)
        self.__stream = None
    def __enter__(self):
        return self.open()
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        
    @property
    def size(self) -> int:
        if self.exists:
            return MemorySize(os.stat(self.path).st_size)
    @property
    def mime(self) -> str|type(None):
        return match.MIME if (match := ft.guess(self.path)) else None
    @property
    def kind(self) -> str|type(None):
        return self.mime.split('/')[0] if (match:=ft.guess(self.path)) else None
    @property
    def ext(self) -> str:
        return os.path.splitext(self.name)[1]
    @property
    def title(self) -> str:
        """
        return the File's name without the extension
        """
        return os.path.splitext(self.name)[0]
    def open(self, mode='r', lines=False, buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None) -> io.TextIOWrapper|io.BufferedReader:
        """
        Return the File's byte or text stream.
        Scrape splits the text at all whitespace and returns the content as a string
        """
        fobj = open(self.path, mode, buffering, encoding, errors, newline, closefd, opener)
        self.__stream = fobj
        return self.__stream
    def close(self) -> _File:
        if self.__stream:
            self.__stream.close()
            self.stream = None
        return self
    def cat(self, text:bool=True, lines:bool=False, copy:bool=False) -> str|bytes|list[str|bytes]:
        """
        Mimmicks the unix command. 
        
        Params
            lines
                whether or not you would like to read the lines (instead of the uninterrupted stream)
            For other args, please refer to help (io.open)
        """
        return shell.cat(self.path, lines=lines, copy=copy)


class Items:
    """
    A wrapper on a directory's content which makes it easier to access by turning elements into attributes
    """
    def __init__(self, path):
        self.path = os.path.realpath(path)
    def __getattr__(self, attr):
        return Place(self.path)[attr]


class Place(Thing):
    """
    Place('.') == Place(os.getcwd())
    """
    def __init__(self, path:str='NewPlace'):
        if path=='.':
            path = os.getcwd()
        elif path == 'NewPlace':
            path = shell.namespacer(path)
        elif path == '~':
            path = os.path.expanduser(path)
        path = os.path.abspath(shell.trim(path))
        if os.path.isfile(path):
            raise ValueError("Given path corresponds to a file")
        self.path = os.path.realpath(path)
        super(type(self), self).__init__(path)
        self.index = -1
    def __len__(self):
        return len(os.listdir(self.path))
    def __bool__(self):
        """
        Check if the Place is empty or not
        """
        return len(os.listdir(self.path)) > 0
    def __iter__(self) -> Iterator[_Placefile]:
        return self
    def __next__(self) -> Sequence[_Placefile]:
        if self.index<len(self)-1:
            self.index += 1
            return self.content[self.index]
        self.index = -1
        raise StopIteration
    def __getitem__(self, item:str|int) -> _Path:
        """
        Return an object whose name is an exact match for the given item
        Params
            items
                int -> calls os.listdir and returns the item'th element
                str -> checks if the item is reachable through self.path and returns if possible
        """
        if isinstance(item, int):
            return os.listdir(self.path)[item]
        elif isinstance(item, str):
            if os.path.isabs(item):
                if os.path.dirname(item) == self.path:
                    return Thing(item).obj
            if os.path.exists(path := os.path.join(self.path, item)):
                return Thing(path).obj
        raise ValueError(f'The folder "{self.name}" does not contain anything called "{item}"')
    def __truediv__(self, other:str):
        if isinstance(other, str):
            return Thing(os.path.join(self.path, other)).obj
        raise TypeError(f"Other must be a string")
    def __call__(self, terms, **kwargs) -> Iterator[str]:
        """
        Find files under self.path matching the given terms/criteria

        Params
            Args
                terms:str
                    the terms sought after. an empty string simply walks
            Kwargs
                exts:str
                    any file extensions you wish to check for, separate by spaces
                case:bool
                    toggle case sensitivity, assumes True if any terms are upper cased
                negative:bool - kwarg
                    Any files/folders with names or extensions matching the terms and exts will be omitted.
                dirs:int
                    0 -> ignore all directories
                    1 -> directories and files
                    2 -> directories only
                strict:int
                    0 -> match any terms in any order
                    1 -> match all terms in any order (interruptions allowed)
                    2 -> match all terms in any order (no interruptions allowed)
                    3 -> match all terms in given order (interruptions)
                    4 -> match all terms in given order (no interruptions)
                    combinations of the following are not counted as interruptions:
                        [' ', '_', '-']
                regex:bool
                    if true, the term-string will be compiled immediately with no further processing.
                    don't forget to set case=True if need be!
                names:bool
                    True -> only yield results whose names match
                    False -> yield results who match at any level
        """
        # yield from Searcher(terms, ext='', folders=False, absolute=True, case=False, strict=True)(self.path)
        # yield from walking.search(self.path, terms, exts=exts, folders=folders, absolute=absolute, case=case, strict=strict, regex=regex, names=names)
        yield from walking.search(self.path, terms, **kwargs)
    def gather(self, dirs:bool=False, absolute:bool=True) -> Iterator[str]:
        """
        Generate an iterable of the files rooted in a given folder. The results will be strings, not File objects
        It is possible to search for multiple File extensions if you separate each one with a space, comma, asterisk, or tilde. 
        Only use one symbol per gathering though.
        
        :param titles: if you only want to know the names of the files gathered, not their full paths
        :param walk: if you want to recursively scan subdiretories
        :param ext: if you want to filter for particular extensions
        """
        yield from walking.walk(self.path, dirs=dirs, absolute=True)
    @property
    def items(self) -> Items:
        """
        This extension allows you to call folder contents as if they were attributes. 
        Will not work on any files/folders whose names wouldn't fly as python variables/attributes
        example:
            >>> folder.items.subfolder
        """
        return Items(self.path)
    @property
    def children(self) -> _Place:
        """
        Return "os.listdir" but filtered for directories
        """
        return (addy.obj for i in os.listdir(self.path) if (addy:=Thing(os.path.join(self.path, i))).isdir)
    @property
    def files(self) -> Iterator[File]:
        """
        Return "os.listdir" but filtered for Files
        """
        return (addy.obj for i in os.listdir(self.path) if (addy:=Thing(os.path.join(self.path, i))).isfile)
    @property
    def content(self) -> Iterator[Thing]:
        """
        Return address-like objects from "os.listdir"
        """
        return tuple(Thing(os.path.join(self.path, i)).obj for i in os.listdir(self.path))
    @property
    def leaves(self) -> Iterator[File]:
        """
        Return All Things from all branches
        """
        yield from map(lambda x: Thing(x).obj, walking.files(self.path, absolute=True))
    @property
    def branches(self) -> Iterator[_Place]:
        """
        Return Every Place whose path contains "self.path"
        """
        yield from map(lambda x: Thing(x).obj, walking.folders(self.path, absolute=True))
    @property
    def size(self) -> MemorySize:
        """
        Return the sum of sizes of all files in self and branches
        """
        return MemorySize(sum(file.size for file in self.leaves))
    @property
    def mimes(self) -> tuple[str]:
        """
        Return Thing mimes for all Things from all branches
        """
        return tuple(unique(filter(None, (File(path).mime for path in self.gather(dirs=False, absolute=True)))))
    @property
    def kinds(self) -> tuple[str]:
        """
        Return Thing types for all Things from branches
        """
        return tuple(m.split('/')[1] for m in self.mimes)
    @property
    def exts(self) -> tuple[str]:
        """
        Return extensions for all Things from all branches
        """
        return tuple(unique(filter(None, (File(path).ext for path in self.gather(dirs=False, absolute=True)))))
    @property
    def isroot(self) -> bool:
        """
        Return check if the Place is at the highest level of the Thing system
        """
        return not self.depth
    
    
    def add(self, other:Address, copy:bool=False) -> _Place:
        """
        Introduce new elements. Send an address-like object to self.
        """
        if isinstance(other, (str, SYSTEM_PATH)):
            other = Thing(str(other)).obj
        if not self.exists:
            raise OSError(f"{self.__short_repr} does not exist")
        if not other.exists:
            raise OSError(f"{other.__short_repr} does not exist")
        new = os.path.join(self.path, os.path.split(other.path)[-1])
        other.clone(folder=self.up.path) if copy else other.rename(new)
        return self
    
    def enter(self) -> _Place:
        """
        Set referent as current working Directory
        """
        if self.exists:
            os.chdir(self.path)
            return self
        raise OSError(f"{self.__short_repr} does not exist")
Directory = Folder = Place

# class Archive(Thing):
    # def __init__(self, path:str='NewThing'):
        # path = os.path.abspath(shell.trim(path))
        # super(Thing, self).__init__(path)
# class Searcherable:

class Audio(File):
    def __init__(self, path:str):
        path = os.path.abspath(shell.trim(path))
        if os.path.isdir(path) or not ft.audio_match(path):
            raise ValueError("Given path corresponds to a directory")
        super(type(self), self).__init__(path)
    @property
    def metadata(self):
        return am.load(self.path)
    @property
    def tags(self):
        self.metadata['tags']
    @property
    def pictures(self):
        self.metadata['pictures']
    @property
    def streaminfo(self):
        self.metadata['streaminfo']
    
    @property
    def artist(self):
        return self.tags['artist']
    @property
    def album(self):
        return self.tags['album']
    @property
    def title(self):
        return self.tags['title']
    
if __name__ == '__main__':
    # show(locals().keys())
    
    
    fp = r'c:\users\kenneth\pyo_rec.wav'
    dp = r'c:\users\kenneth\videos'
    
    d = Place(dp)
    f = Thing(fp)
    tf = Thing('testfile.ext')
    td = Place('testdir')
    
    system = (d, f)
    # show(d('slowthai', sort=True))
    # show(d('alix melanie', sort=True))
    # show(d('melanie alix', sort=True))
    
    # print(formats['all'])
    # for v in formats.values():
        # print(' '.join(v))
        
    