"""
File management wrappers on os.path, shutil, and useful non-standard modules

"Apparent drive" refers to the term before the first os.sep in an object's given path.
    if the given path is relative
        then the ADrive may be ".." or the name of the File/Directory
    else
        the drive is the name/letter of the disk partition on which the content at the address is stored.
"Apparent Directory" similarly refers first term before the last os.sep in an object's given path
    if the given path is relative
        then the ADir may be ".." or the name of the File/Directory
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
__all__ = 'Address Directory File'.split()

from itertools import chain
from typing import Iterable, List, Dict
import os, re, sys, shutil

import filetype as ft, audio_metadata as am
from send2trash import send2trash

from .utils import *

generator = type(i for i in range(0))
function = type(ft.match)

formats = {
    'pics': "bmp png jpg jpeg tiff".split(),
    'music': "mp3 m4a wav ogg wma flac aiff alac".split(),
    'videos': "mp4 wmv".split(),
    'docs': "doc docx pdf xlsx pptx ppt xls csv".split(),
}
formats['all'] = [*chain.from_iterable(formats.values())]

class MemorySize(int):
    """
    Why should you have to sacrifice utility for readability?
    """
    def __repr__(self):
        return nice_size(self)

class Address:
    """
    Base class for a non-descript path-string. 
    Relative paths are not currently supported
    Methods return self unless otherwise stated
    """
    def __init__(self, path:str):
        self.path = path = normalize(path)
        # if not os.path.exists(path):
            # print(Warning(f'Warning: Path "{path}" does not exist'))
    def __str__(self):
        return self.path
    def __hash__(self):
        return hash(self.path)
    def __repr__(self):
        # return self.path
        # tipo = "Directory File".split()[self.isfile]
        return f"{tipo(self)}(name={self.name}, up={self.up.name})"
    
    def create(self, content:[str, bytes, bytearray]=None, raw:bool=False):
        """
        Create an entry in the file-system. If the address is not vacant no action will be taken.
        The raw handle only works for Files and enables writing bytes/bytearrays
        """
        if self.exists:
            return self
        elif content:
            os.makedirs(self.up.path, exist_ok=True)
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
        else:
            os.makedirs(self.up.path, exist_ok=True)
            if likefile(self.path):
                with open(self.path, 'x') as fobj:
                    pass
            else:
                os.makedirs(self.path)
        return self
    
    @property
    def exists(self):
        return os.path.exists(self.path)
    @property
    def isdir(self):
        if self.exists:
            return os.path.isdir(self.path)
        elif type(self) == type(Directory('.')):
            return True
        elif type(self) == type(File('a')):
            return False
        return not likefile(self.path)
    @property
    def isfile(self):
        if self.exists:
            return os.path.isfile(self.path)
        elif type(self) == type(File('a')):
            return True
        elif type(self) == type(Directory('.')):
            return False
        return likefile(self.path)
    
    @property
    def obj(self):
        """
        Determine if self.path points to a file or folder and create the corresponding object
        """
        if self.exists:
            return File(self.path) if os.path.isfile(self.path) else Directory(self.path)
        else:
            return File(self.path) if likefile(self.path) else Directory(self.path)
    @property
    def up(self):
        """
        Return the ADir
        """
        return Address(delevel(self.path)).obj
    @property
    def name(self):
        """
        Return the name of the referent
        """
        return os.path.split(self.path)[1]
    
    @property
    def ancestors(self):
        """
        Return consecutive ADirs until the ADrive is reached
        """
        level = []
        p = self.path[:]
        while p != delevel(p):
            p = delevel(p)
            level.append(p)
        return tuple(Address(i).obj for i in level)[::-1]
    @property
    def colleagues(self):
        """
        Every member of the same Directory whose type is the same as the referent
        """
        return (i for i in self.up if isinstance(i, type(self)))
    @property
    def neighbours(self):
        """
        Everything in the same Directory
        """
        return self.up.content
    @property
    def depth(self):
        """
        Number of ancestors
        """
        return len(self.ancestors)
    @property
    def top(self):
        """
        The apparent drive. Will not be helpful if self.path is relative
        """
        return self.ancestors[0]
    @property
    def stat(self):
        """
        return os.stat(self.path) 
        """
        return os.stat(self.path)
        
    def delevel(self, steps:int=1, path:bool=False) -> str:
        """
        Go up some number of levels in the File system
        """
        return delevel(self.path, steps) if path else Directory(delevel(self.path, steps))
    @property
    def ancestry(self):
        """
        A fancy representation of the tree from the apparent drive up to the given path
        """
        print(f'ancestry({self.name})')
        ancs = list(self.ancestors[1:])
        # ancs = self.ancestors[1:]
        ancs.append(self.path)
        # print(ancs)
        for i, anc in enumerate(ancs):
            print('\t' + ('', '.'*i)[i>0] + i*'  ' + [i for i in str(anc).split(os.sep) if i][-1] + '/')
        return self
    def touch(self):
        """
        Implements the unix command 'touch', which updates the 'date modified' of the content at the path
        """
        p = self.path
        pathlib.Path(p).touch()
        self = Address(p).obj
        return self
    def erase(self, recycle:bool=True):
        """
        Send a File to the trash, or remove it without recycling.
        """
        send2trash(self.path) if recycle else os.remove(self.path)
        return self
    def clone(self, folder:str=None, name:str=None, cwd:bool=False, sep:str='_', touch=False):
        """
        Returns a clone of the referent at a given Directory-path
        The given path will be created if it doesn't exist
        Will copy in the File's original folder if no path is given
        The cwd switch will always copy to the current working Directory
        """
        copier = (shutil.copy2, shutil.copytree)[self.isdir]
        if cwd:
            new = os.path.join(os.getcwd(), name if name else self.name)
        elif folder:
            new = os.path.join(folder, name if name else self.name)
        else:
            new = self.path
        new = nameSpacer(new, sep=sep)
        os.makedirs(delevel(new), exist_ok=True)
        copier(self.path, new)
        out = Address(new).obj
        return out.touch() if touch else out
    def move(self, folder:str=None, name:str=None, dodge:bool=False, sep:str='_', recycle:bool=True):
        """
        addy.move(folder) -> move to the given Directory ()
        addy.move(name) -> move to the given path (relative paths will follow from the objects existing path)
        addy.move(folder, name) -> move to the given Directory 
        
        :param dodge: 
            enables automatic evasion of file-system collisions
        :param sep: 
            chooses the separator you use between the object's name and numerical affix in your directory's namespace
            **inert if dodge is not True
        :param recycle: 
            enables you to avoid the PermissionError raised by os.remove (if you have send2trash installed)
            ** the PermissionError is due to the object being in use at the time of attempted deletion
       """
        if folder and name:
            os.makedirs(folder, exist_ok=True)
            new = os.path.join(folder, name)
        elif folder:
            os.makedirs(folder, exist_ok=True)
            new = os.path.join(folder, self.name)
        elif name:
            new = os.path.join(self.up.path, name)
        else:
            raise ValueError(f'The file couldn\'t be moved because {name=} and {folder=}. Set either one or both')
        new = nameSpacer(new, sep=sep) if dodge else new
        folder, name = os.path.split(new)
        self.clone(folder=folder, name=name)
        # os.remove(self.path)
        self.erase()
        self.path = new
        return self
    def rename(self, name:str):
        """
        Change the name of the referent
        """
        return self.move(name=name)
    def expose(self):
        """
        Reveal the referent in the system's file explorer (will open the containing Directory if the referent is a File)
        """
        if self.isdir:
            os.startfile(self.path)
        else:
            os.startfile(self.up.path)
        return self


class File(Address):
    """
    Create a new File object for context management and ordinary operations
    """
    def __init__(self, path:str='NewFile'):
        path = os.path.abspath(trim(path))
        super(File, self).__init__(path)
        self._stream = None
    def __enter__(self):
        return self.open()
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def __repr__(self):
        # return self.path
        # tipo = "Directory File".split()[self.isfile]
        return f"{tipo(self)}(name={self.name}, up={self.up.name}, size={self.size})"
        
    @property
    def size(self):
        return MemorySize(os.stat(self.path).st_size)
    @property
    def mime(self):
        return match.MIME if (match:=ft.guess(self.path)) else None
    @property
    def kind(self):
        return self.mime.split('/')[0] if (match:=ft.guess(self.path)) else None
    @property
    def ext(self):
        return os.path.splitext(self.name)[1]
    @property
    def title(self):
        """
        return the File's name without the extension
        """
        return os.path.splitext(self.name)[0]
    def open(self, mode:str='r', scrape:bool=False):
        """
        Return the File's byte or text stream.
        Scrape splits the text at all whitespace and returns the content as a string
        """
        if scrape:
            with open(self.path, mode) as fobj:
                return ' '.join(fobj.read().split())
        with open(self.path, mode) as fobj:
            self._stream = fobj
            return self._stream
    def close(self):
        if self._stream:
            self._stream.close()
        return self
    @property
    def run(self):
        os.startfile(self.path)
        return self


class Items:
    """
    A wrapper on a directory's content which makes it easier to access by turning elements into attributes
    """
    def __init__(self, path):
        self.path = normalize(path)
    def __getattr__(self, attr):
        return Directory(self.path)[attr]


class Directory(Address):
    """
    Directory('.') == Directory(os.getcwd())
    """
    def __init__(self, path:str='NewDirectory'):
        if path=='.':
            path = os.getcwd()
        elif path == 'NewDirectory':
            path = nameSpacer(path)
        elif path == '~':
            path = os.path.expanduser(path)
        path = os.path.abspath(trim(path))
        self.path = normalize(path)
        super(Directory, self).__init__(path)
        self.index = -1
    def __repr__(self):
        # return self.path
        # tipo = "Directory File".split()[self.isfile]
        return f"{tipo(self)}(name={self.name}, up={self.up.name})"
    def __len__(self):
        return len(os.listdir(self.path))
    def __bool__(self):
        """
        Check if the Directory is empty or not
        """
        return len(os.listdir(self.path)) > 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.index<len(self)-1:
            self.index += 1
            return self.content[self.index]
        self.index = -1
        raise StopIteration
    def __getitem__(self, item:str):
        """
        Return an object whose name is an exact match for the given item
        """
        if any(re.search(f'^{item}$', i.name, re.I) for i in self.content):
            return Address(os.path.join(self.path, item)).obj
        raise ValueError(f'The folder "{self.name}" does not contain anything called "{item}"')
    def __truediv__(self, other:str):
        if isinstance(other, str):
            return Address(os.path.join(self.path, other)).obj
        raise TypeError(f"Other must be a string")
    def __call__(self, keyword:str, sort:bool=False, case:bool=False, **kwargs) -> Iterable:
        """
        See help(self.search)
        """
        return self.search(keyword, sort, case, **kwargs)
    
    @property
    def items(self):
        """
        This extension allows you to call folder contents as if they were attributes. 
        Will not work if your file system does not use a python-viable naming convention
        example:
            >>> folder.items.subfolder
        """
        return Items(self.path)
    @property
    def children(self):
        """
        Return "os.listdir" but filtered for directories
        """
        return (addy.obj for i in os.listdir(self.path) if (addy:=Address(os.path.join(self.path, i))).isdir)
    @property
    def files(self):
        """
        Return "os.listdir" but filtered for Files
        """
        return (addy.obj for i in os.listdir(self.path) if (addy:=Address(os.path.join(self.path, i))).isfile)
    @property
    def content(self):
        """
        Return address-like objects from "os.listdir"
        """
        return tuple(Address(os.path.join(self.path, i)).obj for i in os.listdir(self.path))
    @property
    def leaves(self):
        """
        Return All Files from all branches
        """
        # return tuple(self.gather())
        return map(lambda x: Address(x).obj, self.gather())
    @property
    def branches(self):
        """
        Return Every Directory whose path contains "self.path"
        """
        return tuple(set(File(i).delevel() for i in self.gather()))
    @property
    def size(self):
        """
        Return the sum of sizes of all files in self and branches
        """
        return MemorySize(sum(file.size for file in self.leaves))
    @property
    def mimes(self):
        """
        Return File mimes for all Files from all branches
        """
        return tuple(set(file.mime for file in self.gather()))
    @property
    def kinds(self):
        """
        Return File types for all Files from branches
        """
        return tuple(set(m.split('/')[0] for m in self.mime))
    @property
    def exts(self):
        """
        Return extensions for all Files from all branches
        """
        return tuple(set(f.ext for f in self.gather()))
    @property
    def isroot(self):
        """
        Return check if the Directory is at the highest level of the File system
        """
        return not self.depth
    
    def add(self, other:Address, copy:bool=False):
        """
        Introduce new elements. Send an address-like object to self.
        """
        if not self.exists:
            raise OSError(f"Cannot add to Directory({self.name}) because it doesn't exist")
        elif not other.exists:
            if issubclass(type(other), Address):
                tipo = 'Directory File'.split()[other.isfile]
            raise OSError(f"{other.name.title()} could not be added to {self.name} because it doesn't exist")
        new = os.path.join(self.path, os.path.split(other.path)[-1])
        other.clone(folder=self.up.path) if copy else other.rename(new)
        return self
    
    def enter(self):
        """
        Set referent as current working Directory
        """
        os.chdir(self.path)
        
    def gather(self, titles:bool=False, walk:bool=True, ext:str='') -> generator:
        """
        Generate an iterable of the files rooted in a given folder. The results will be strings, not File objects
        It is possible to search for multiple File extensions if you separate each one with a space, comma, asterisk, or tilde. 
        Only use one symbol per gathering though.
        
        :param titles: if you only want to know the names of the files gathered, not their full paths
        :param walk: if you want to recursively scan subdiretories
        :param ext: if you want to filter for particular extensions
        """
        folder = self.path
        if walk:
            if ext:
                ext = ext.replace('.', '')
                sep = [i for i in ',`* ' if i in ext]
                pattern = '|'.join(f'\.{i}$' for i in ext.split(sep[0] if sep else None))
                pat = re.compile(pattern, re.I)
                for root, folders, names in os.walk(folder):
                    for name in names:
                        if os.path.isfile(p:=os.path.join(root, name)) and pat.search(name) and name!='NTUSER.DAT':
                            yield name if titles else p
            else:
                for root, folders, names in os.walk(folder):
                    for name in names:
                        if os.path.exists(p:=os.path.join(root, name)):
                            yield name if titles else p
        else:
            if ext:
                ext = ext.replace('.', '')
                sep = [i for i in ',`* ' if i in ext]
                pattern = '|'.join(f'\.{i}$' for i in ext.split(sep[0] if sep else None))
                pat = re.compile(pattern, re.I)
                for name in os.listdir(folder):
                    if os.path.isfile(p:=os.path.join(folder, name)) and pat.search(name) and name!='NTUSER.DAT':
                        yield name if titles else p
            else:
                for name in os.listdir(folder):
                    if os.path.isfile(p:=os.path.join(folder, name)):
                        yield name if titles else p
    
    def search(self, keyword:str, sort:bool=False, case:bool=False, prescape:bool=False, strict:bool=True, **kwargs) -> Iterable:
        """
        Return an iterator of Files whose path match the given keyword within a Directory.
        The search is linear and the sorting is based on the number of matches. If sorted, a list will be returned.
        Case pertains to case-sensitivity
        Prescape informs the method that kewords do not need to be escaped
        For kwargs see help(self.gather)
        
        :param keyword: terms you wish to match, separated by spaces
        :param sort: if you would like to sort the results by number of matches
        :param case: if you would like to make the search case sensitive
        :param prescape: if you have already re.escape-d the terms you would like to search
        :param strict: if you only want to see results which match every term in the keyword string
        """
        casesensitivity = (re.I, 0)[case]
        escaper = (re.escape, lambda x: x)[prescape]
        if isinstance(keyword, str):
            keyword = keyword.split()
        if not isinstance(keyword, str):
            keyword = '|'.join(map(escaper, keyword))
        if strict:
            return filter(
                lambda x: len([*re.finditer(keyword, x, casesensitivity)]) >= len(keyword.split('|')),
                self.gather(**kwargs),
            )
        elif sort:
            return sorted(
                filter(
                    lambda x: len([*re.finditer(keyword, x, casesensitivity)]) == len(keyword.split('|')),
                    self.gather(**kwargs),
                ),
                key=lambda x: len([*re.finditer(keyword, x, casesensitivity)]),
                reverse=True
            )
        else:
            return filter(
                lambda x: re.search(keyword, x, casesensitivity),
                self.gather(**kwargs)
            )


# class Archive(Address):
    # def __init__(self, path:str='NewFile'):
        # path = os.path.abspath(trim(path))
        # super(File, self).__init__(path)

if __name__ == '__main__':
    show(locals().keys())
    
    
    fp = r'c:\users\kenneth\pyo_rec.wav'
    dp = r'c:\users\kenneth\videos'
    
    d = Directory(dp)
    f = File(fp)
    tf = File('testfile.ext')
    td = Directory('testdir')
    
    system = (d, f)
    # show(d('slowthai', sort=True))
    # show(d('alix melanie', sort=True))
    # show(d('melanie alix', sort=True))
    
    # print(formats['all'])
    # for v in formats.values():
        # print(' '.join(v))
        
    