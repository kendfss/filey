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
"""

from pathlib import Path
from functools import reduce, cached_property
from itertools import chain
from typing import Iterable
import os, re, sys, shutil


import filetype as ft, audio_metadata as am
from send2trash import send2trash



from sl4ng import show, delevel, gather, nameSpacer, ffplay, commons, nopes
# from magnitudes import represent# as rp


gen = type(i for i in range(0))
func = type(ft.match)

forbiddens = r'\/:?*<>|"' # at least on windows

formats = {
    'pics': "bmp png jpg jpeg tiff".split(),
    'music': "mp3 m4a wav ogg wma flac aiff alac".split(),
    'videos': "mp4 wmv".split(),
    'docs': "doc docx pdf xlsx pptx ppt xls csv".split(),
}
formats['all'] = [*chain.from_iterable(formats.values())]




def trim(path:str, edge:str=os.sep) -> str:
    out = path[:]
    while out.startswith(edge):
        out = out[1:]
    while out.endswith(edge):
        out = out[:-1]
    return out

def normalize(path:str, relative:bool=False) -> str:
    other = ''.join(i for i in '\/' if not i==os.sep)
    if other in path:
        terms = []
        for term in path.split(os.sep):
            if other in term:
                for part in term.split(other):
                    terms.append(part)
            else:
                terms.append(term)
        path = os.path.join(*terms)
    if relative:
        path = '.'+os.sep+path
    return path

def hasdirs(path:str) -> bool:
    return bool(re.search(re.escape(os.sep), normalize(path)))

def likeFile(path:str) -> bool:
    path = normalize(path)
    return bool(re.search('readme$|.+\.(\S)+$',path.split(os.sep)[-1],re.I))

def multisplit(splitters:Iterable[str], target:str) -> gen:
    """
    Split a string by a the elements of a sequence
    >>> list(multisplit(',`* ', 'wma,wmv mp3`vga*mp4 ,`*  ogg'))
    ['wma', 'wmv', 'mp3', 'vga', 'mp4', 'ogg']
    """
    splitters = iter(splitters)
    result = target.split(next(splitters))
    for splitter in splitters:
        result = [*chain.from_iterable(i.split(splitter) for i in result)]
    yield from filter(None, result)

class Address:
    """
    Methods return self unless otherwise stated
    """
    def __init__(self, path:str):
        self.path = path = normalize(path)
        # if not os.path.exists(path):
            # print(Warning(f'Warning: Path "{path}" does not exist'))
    def __str__(self):
        return self.path
    def __repr__(self):
        return self.path
    def __hash__(self):
        return hash(self.path)
    
    def create(self, content:[str, bytes, bytearray]=None, raw:bool=False):
        """
        Create an entry in the file-system. If the address is not vacant no action will be taken.
        The raw handle only works for Files and enables writing bytes/bytearrays
        """
        if self.exists:
            return self
        elif content:
            if raw:
                if isinstance(content,(bytes,bytearray)):
                    fobj = open(self.path,'wb')
                else:
                    fobj = open(self.path,'w')
                fobj.write(content)
                fobj.close()
            else:
                if isinstance(content,str):
                    content = bytes(content,encoding='utf-8')
                else:
                    content = bytes(content)
                with open(self.path,'wb') as fobj:
                    fobj.write(content)
        else:
            if likeFile(self.path):
                with open(self.path,'x') as fobj:
                    pass
            else:
                os.makedirs(self.path,exist_ok=True)
        return self
    
    @property
    def exists(self):
        return os.path.exists(self.path)
    @property
    def isdir(self):
        if self.exists:
            return os.path.isdir(self.path)
        return not likeFile(self.path)
    @property
    def isfile(self):
        if self.exists:
            return os.path.isdir(self.path)
        return likeFile(self.path)
    
    @property
    def obj(self):
        """
        Determine if self.path points to a file or folder and create the corresponding object
        """
        if self.exists:
            return File(self.path) if os.path.isfile(self.path) else Directory(self.path)
        else:
            return File(self.path) if likeFile(self.path) else Directory(self.path)
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
        return tuple(i for i in self.up if isinstance(i, type(self)))
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
        return delevel(self.path,steps) if path else Directory(delevel(self.path,steps))
    def heritage(self):
        """
        A fancy representation of the tree from the apparent drive up to the given path
        """
        print(f'\nheritage({self.name.title()})')
        ancs = list(self.ancestors)
        ancs.append(self.path)
        for i,anc in enumerate(ancs):
            print('\t' + ('','.'*i)[i>0] + i*'  ' + [i for i in str(anc).split(os.sep) if i][-1])
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
    def copy(self, folder:str=None, cwd:bool=False, sep:str='_'):
        """
        Returns a clone of the referent at a given Directory-path
        The given path will be created if it doesn't exist
        Will copy in the File's original folder if no path is given
        The cwd switch will always copy to the current working Directory
        """
        copier = (shutil.copy2, shutil.copytree)[self.isdir]
        if folder:
            new = os.path.join(folder, self.name)
        elif cwd:
            new = os.path.join(os.getcwd(), self.name)
        else:
            new = self.path
        new = nameSpacer(new, sep=sep)
        os.makedirs(delevel(new), exist_ok=True)
        copier(self.path, new)
        out = Address(new).obj
        return out.touch() if touch else out
    def move(self, folder:str=None, name:str=None, dodge:str=False, sep:str='_'):
        """
        addy.move(folder) -> move to the given Directory ()
        addy.move(name) -> move to the given path (relative paths will follow from the objects existing path)
        addy.move(folder, name) -> move to the given Directory 
        
        The dodge handle enables automatic file-system collision evasion
        """
        if folder and name:
            new = os.path.join(folder, name)
        elif folder:
            new = os.path.join(folder, self.name)
        elif name:
            new = os.path.join(self.up.path, name)
        else:
            raise ValueError('The file couldn\'t be moved because "name" and "folder" are undefined')
        new = nameSpacer(new, sep=sep) if dodge else new
        os.rename(self.path, new)
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
            os.startFile(self.path)
        else:
            os.startFile(self.up.path)
        return self

class File(Address):
    def __init__(self,path:str):
        path = os.path.abspath(trim(path))
        super(File,self).__init__(path)
        self._stream = None
    def __enter__(self):
        self._stream = open(str(self),'b')
        return self._stream
    def __exit__(self, exc_type, exc_value, traceback):
        self._stream.close()
        self._stream = None
        
    @property
    def size(self):
        return size(os.stat(self.path).st_size)
    @property
    def mime(self):
        return match.MIME if (match:=ft.guess(str(self))) else None
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
    def open(mode:str='r', scrape:bool=False):
        """
        Return the File's byte or text stream.
        Scrape splits the text at all whitespace and returns the content as a string
        """
        if scrape:
            with open(self.path, mode) as fobj:
                return ' '.join(fobj.read().split())
        with open(self.path, mode) as fobj:
            return fobj
    
class Directory(Address):
    def __init__(self, path:str):
        path = os.path.abspath(trim(path))
        self.path = normalize(path)
        super(Directory, self).__init__(path)
        self._ind = -1
    def __len__(self):
        return len(self.content)
    def __bool__(self):
        """
        Check if the Directory is empty or not
        """
        return len(os.listdir(self.path))>0
    def __iter__(self):
        return self
    def __next__(self):
        if self._ind<len(self)-1:
            self._ind += 1
            return self.content[self._ind]
        self._ind = -1
        raise StopIteration
    def __getitem__(self, item):
        """
        Return an object whose name is an exact match for the given item
        """
        if any(re.search(f'^{item}$', i.name, re.I) for i in self.content):
            return Address(os.path.join(self.path, item)).obj
        raise ValueError(f'The folder "{self.name}" does not contain anything called "{item}"')
    def __truediv__(self, other):
        if isinstance(other, str):
            return Address(os.path.join(self.path, other)).obj
        raise TypeError(f"Other must be a string")
    def __call__(self, keyword:str, sort:bool=False, case:bool=False, **kwargs) -> Iterable:
        """
        See help(self.search)
        """
        return self.search(keyword, sort, case, **kwargs)
    @property
    def children(self):
        """
        Return "os.listdir" but filtered for directories
        """
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=Address(os.path.join(str(self),i))).isdir)
    @property
    def files(self):
        """
        Return "os.listdir" but filtered for Files
        """
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=Address(os.path.join(self.path,i))).isfile)
    @property
    def content(self):
        """
        Return address-like objects from "os.listdir"
        """
        return tuple(Address(os.path.join(self.path,i)).obj for i in os.listdir(self.path))
    @property
    def leaves(self):
        """
        Return All Files from all branches
        """
        return tuple(self.gather())
    @property
    def branches(self):
        """
        Return Every Directory whose path contains "self.path"
        """
        return tuple(set(i.delevel() for i in self.gather()))
    @property
    def size(self):
        """
        Return Prettified version of _size
        """
        return sum(File.size for File in self.leaves)
    @property
    def _size(self):
        """
        Return sum of File sizes for all leaves
        """
        return sum(File.size for File in self.leaves)
    @property
    def mimes(self):
        """
        Return File mimes for all Files from all branches
        """
        return tuple(set(File.mime for File in self.gather()))
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
    
    def add(self, other, copy=False):
        """
        Introduce new elements. Send an address-like object to self.
        """
        if not other.exists:
            raise OSError(f"{other.name.title()} could not be added to {self.name.title()} because it doesn't exist")
        new = os.path.join(self.path, os.path.split(other.path)[-1])
        other.rename(new)
        return self
    
    def enter(self):
        """
        Set referent as current working Directory
        """
        os.chdir(self.path)
        
    def gather(self, titles:bool=False, walk:bool=True, ext:str='') -> gen:
        """
        Generate an iterable of the Files rooted in a given folder
        It is possible to search for multiple File extensions if you separate each one with a space, comma, asterisk, or tilde. 
        Only use one symbol per gathering though.
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
    
    def search(self, keyword:str, sort:bool=False, case:bool=False, prescape:bool=False, **kwargs) -> Iterable:
        """
        Return an iterator of Files whose path match the given keyword within a Directory.
        The search is linear and the sorting is based on the number of matches. If sorted, a list will be returned.
        Case pertains to case-sensitivity
        Prescape informs the method that kewords do not need to be escaped
        For kwargs see help(self.gather)
        """
        casesensitivity = (re.I, 0)[case]
        escaper = (re.escape, id)[prescape]
        if isinstance(keyword, str):
            keyword = keyword.split()
        if not isinstance(keyword, str):
            keyword = '|'.join(map(escaper, keyword))
        if sort:
            return sorted(
                filter(
                    # lambda x: re.search(keyword, x, casesensitivity),
                    lambda x: len([*re.finditer(keyword, x, casesensitivity)]) == len(keyword.split('|')),
                    self.gather(**kwargs),
                ),
                key=lambda x: len([*re.finditer(keyword, x, casesensitivity)]),
                reverse=True
            )
        else:
            return filter(
                # lambda x: re.finditer(keyword, x, casesensitivity),
                lambda x: re.search(keyword, x, casesensitivity),
                self.gather(**kwargs)
            )
if __name__ == '__main__':
    mock = 'drive: users user place subplace File.extension.secondextension'.split()
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
    show(zip(map(type,map(lambda x: Address(x).obj, testPaths)),testPaths))
    # show(zip(testPaths,map(normalize,testPaths)))
    # show(zip(testPaths,map(hasdirs,testPaths)))
    # show(zip(testPaths,map(likeFile,testPaths)))
    
    # ddemo = Address(os.path.join(*mock[:-1])).obj
    # fdemo = Address(os.path.join(*mock)).obj
    # ddemo = Directory(os.path.join(*mock[:-1]))
    # fdemo = File(os.path.join(*mock))
    
    fp = r'c:\users\kenneth\pyo_rec.wav'
    dp = r'c:\users\kenneth\videos'
    
    d = Directory(dp)
    f = File(fp)
    
    system = (d, f)
    show(d('slowthai',sort=True))
    show(d('alix melanie', sort=True))
    
    print(formats['all'])
    for v in formats.values():
        print(' '.join(v))