"""
Implementation of a rudimentary file system

TODO:
    grab the
"""

import os, sys, shutil, pathlib, re
from dataclasses import dataclass

import filetype as ft
from send2trash import send2trash

from sl4ng import show, delevel, gather, nameSpacer, ffplay, commons, nopes
# from magnitudes import rep
from .magnitudes import represent# as rp
# from magnitudes import *

forbiddenChars = r'\/:?*<>|"'

formats = {
    'pics':['bmp','png','jpg','jpeg','tiff',],
    'music':['mp3','m4a','wav','ogg','wma','flac','aiff','alac',],
    'videos':['mp4','wmv',],
    'docs':['doc','docx','pdf','xlsx','pptx','ppt','xls','csv',],
}

orders = {
    1:'deca',
    2:'hecto',
    3:'kilo',
    6:'mega',
    9:'giga',
    12:'tera',
    15:'peta',
    18:'exa',
    21:'zetta',
    24:'yotta'
}

def trim(path,edge=os.sep):
    out = path[:]
    while out.startswith(edge):
        out = out[1:]
    while out.endswith(edge):
        out = out[:-1]
    return out


# @dataclass
# class size:
    # val:int
class size(int):
    # def __repr__(self):
        # rep = round(self*10**-3)
        # if len(st)
        # return f'{round(self*10**-3):,} kb'
    def __repr__(self):
        return rp(self)
    # def __str__(self):
        # return str(self.val)
    # def __add__(self,other):
        # return self.val + size(other)
    # def __truediv__(self,other):
        # return self.val + size(other)
    # def __sub__(self,other):
        # return self.val + size(other)
    # def __mul__(self,other):
        # return self.val + size(other)
    # pass
    # def __str__(self):
        # return str(int(self))
    # def __repr__(self,dim='bytes',long=False,lower=False,precision=2,sep='-'):
        # orders = {
            # 3:'kilo',
            # 6:'mega',
            # 9:'giga',
            # 12:'tera',
            # 15:'peta',
            # 18:'exa',
            # 21:'zetta',
            # 24:'yotta',
        # }

        # sredro = {v:k for k,v in orders.items()}

        # pretty = lambda number,unit='': f'{number:,} {unit}'.strip()
        # setcase = lambda unit,lower=False: [unit.upper().strip(),unit.lower().strip()][lower]
        # setlength = lambda mag,dim,long=False,sep='-': ('',sep)[long].join(((mag[0],dim[0]),(mag,dim))[long])
        
        
        # mags = tuple(sorted(orders.keys()))
        # booly = lambda i: len(str(int(self))) < len(str(10**mags[i+1]))
        # fits = tuple(nopes((booly(i) for i in range(len(mags)-1)),True))
        # fits = tuple(filter(booly,range(len(mags)-1)))
        # mag = orders[mags[min(fits) if fits else len(mags)-1]]
        # unit = setcase(setlength(mag,dim,long,['',sep][long]),lower)
        # number = round(self*10**-sredro[mag],precision)
        # return pretty(number,unit).lower() if lower else pretty(number,unit).upper()
@dataclass
class _pathLike:
    path:str
    
    def __str__(self):
        return self.path
    def __repr__(self):
        return str(self)
    def __hash__(self):
        return hash(str(self))
    
    @property
    def exists(self):
        return os.path.exists(self.path)
    @property
    def up(self):
        return address(delevel(str(self))).obj
    @property
    def name(self):
        return os.path.split(self.path)[1]
    @property
    def title(self):
        return os.path.splitext(self.name)[0]
    @property
    def ancestors(self):
        level = []
        p = self.path[:]
        while p != delevel(p):
            p = delevel(p)
            level.append(p)
        return tuple(address(i).obj for i in level)[::-1]
    @property
    def siblings(self):
        # return tuple(i for i in self.delevel() if isinstance(i,type(self)))
        return tuple(i for i in self.up if isinstance(i,type(self)))
    @property
    def depth(self):
        return len(self.ancestors)
    @property
    def root(self):
        return self.ancestors[0]#.split(':')[0]
    @property
    def peers(self):
        return self.delevel().content
    @property
    def stat(self):
        """
       return os.stat(str(self)) 
        """
        return os.stat(str(self))
        
    def delevel(self,steps=1,path=False):
        return delevel(self.path,steps) if path else directory(delevel(self.path,steps))
    def heritage(self):
        print(f'\nheritage({self.name.title()})')
        ancs = list(self.ancestors)
        ancs.append(self.path)
        for i,anc in enumerate(ancs):
            print('\t'+('','.'*i)[i>0]+i*'  '+[i for i in str(anc).split(os.sep) if i][-1])
    
    def touch(self):
        p = str(self)
        pathlib.Path(p).touch()
        self = address(p).obj
        return self
    def delete(self,recycle=True):
        send2trash(self.path) if recycle else os.remove(self.path)
        del self
    def rename(self,new,relative=False):
        new = new if not relative else os.path.join(delevel(self.path),new)
        os.makedirs(delevel(new),exist_ok=True)
        os.rename(self.path,new)
        self = address(new).obj
        return self
    def clone(self,new=None,relative=False,touch=False):
        if new:
            if relative:
                new = nameSpacer(os.path.join(delevel(self.path),new))
        else:
            new = nameSpacer(os.path.join(delevel(self.path),self.name))
        os.makedirs(delevel(new),exist_ok=True)
        shutil.copy2(self.path,new) #if touch else shutil.copy2(self.path,new)
        out = address(new).obj
        return out.touch() if touch else out
    
    move = rename
    copy = clone
    

@dataclass
class address(_pathLike):
    """
    A systemic pointer to the location of the data associated with a file system object
    """
    def __init__(self,path:str):
        super(address,self).__init__(path)
        # assert os.path.exists(path), f'"{path}" is not a valid address on this system'
        assert self.exists, f'"{path}" is not a valid address on this system'
    
    
    @property
    def isdir(self):
        return os.path.isdir(self.path)
    @property
    def isfile(self):
        return os.path.isfile(self.path)
    @property
    def obj(self):
        if self.isdir:
            return directory(self.path)
        elif self.isfile:
            return file(self.path)
    
    def expose(self):
        os.startfile(self.path)
        return self
    

# class directory(_pathLike):
class directory(address):
    def __init__(self,path:str):
        path = os.path.abspath(trim(path))
        assert address(path)#.isdir, f'"{path}" is not a directory'
        super(directory,self).__init__(path)
        self._ind = -1
        # self.
    def __bool__(self):
        return len(os.listdir(self.path))>0
    def __len__(self):
        return len(self.content)
    def __iter__(self):
        return self
    def __next__(self):
        if self._ind<len(self)-1:
            self._ind += 1
            return self.content[self._ind]
        self._ind = -1
        raise StopIteration
    def __getitem__(self,item):
        if any(re.search(f'^{item}$',i.name,re.I) for i in self.content):
        # for i in nopes((re.search(f'^{item}$',i.name,re.I) for i in self.content),True):
            return address(os.path.join(self.path,item)).obj
        raise ValueError(f'The folder "{self.name}" does not contain anything called "{item}"')
        
    @property
    def children(self):
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=address(os.path.join(str(self),i))).isdir)
    @property
    def files(self):
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=address(os.path.join(self.path,i))).isfile)
    @property
    def content(self):
        return tuple(address(os.path.join(self.path,i)).obj for i in os.listdir(self.path))
    @property
    def leaves(self):
        return tuple(self.gather())
    @property
    def branches(self):
        return tuple(set(i.delevel() for i in self.gather()))
    @property
    def size(self):
        return size(sum(file.size for file in self.leaves))
    @property
    def mime(self):
        return tuple(set(file.mime for file in self.gather()))
    @property
    def kind(self):
        return tuple(set(m.split('/')[0] for m in self.mime))
    @property
    def ext(self):
        return tuple(set(f.ext for f in self.gather()))
    @property
    def isroot(self):
        return not self.depth
    
    def enter(self):
        os.chdir(self.path)
    def gather(self,names:bool=False,walk:bool=True,ext:str=None,paths=False):
        if paths:
            yield from gather(str(self),names,walk,ext)
        else:
            yield from set(file(path) for path in gather(str(self),names,walk,ext))
            # for path in gather(str(self),names,walk,ext):
                # yield file(path)
    def add(self,new):
        if (obj:=address(new).obj):
            return obj.move(self)
        else:
            raise ValueError(f'"{new}" does is neither a file or directory')
    
    def moveContent(self,other):
        # assert address(trim(str(other))).isdir, f'"{other}" is not a viable directory here'
        assert address((str(other))).isdir, f'"{other}" is not a viable directory here'
        for f in self.gather():
            # rest = f.path[len(self.path)+1:]
            ending = trim(f.path[len(self.path)+1:])
            new = os.path.join(trim(str(other)),ending)
            # os.makedirs(delevel(new))
            print(self)
            print(f)
            print(ending)
            print(new)
            print()
    def show(self, indentation:int=1, enum:bool=False, start:int=1, indentor:str='\t'):
        assert indentation>0, f'"{indentation}" is not a viable indentation level'
        print((indentation-1)*'\t'+self.name)
        show(self.content,indentation,enum,start,indentor)
    
    extension = ext  

    
class file(_pathLike):
    def __init__(self,path:str):
        path = os.path.abspath(trim(path))
        assert address(path)#, f'"{path}" is not a file'
        super(file,self).__init__(path)
        self._stream = None
    def __enter__(self):
        self._stream = open(str(self),'b')
        return self
    def __exit__(self):
        self._stream.close()
        self._stream = None
    
    @property
    def size(self):
        return size(os.stat(str(self)).st_size)
    @property
    def mime(self):
        return match.MIME if (match:=ft.guess(str(self))) else 'UNKNOWN'
    @property
    def kind(self):
        return self.mime.split('/')[0] if (match:=ft.guess(str(self))) else 'UNKNOWN'
    @property
    def ext(self):
        return os.path.splitext(self.name)[1]

    extension = ext   


user = directory(commons['home'])
root = user.up.up

if __name__ == '__main__':
    fp = r'c:\users\kenneth\pyo_rec.wav'
    dp = r'c:\users\kenneth\videos'
    
    # fp = r'C:\Users\Kenneth\Music\Collection\slowthai\The Bottom _ North Nights\02 North Nights.mp3'#[:-1]
    # dp = delevel(fp,1)#[:-1]
    
    # d = address(dp).obj
    # f = address(fp).obj
    
    d = directory(dp)
    f = file(fp)
    
    system = (d,f)
    [print(i) for i in system]
    [print(i.size) for i in system]
    print()
    # [show(i.delevel()) for i in system]
    # [show(i.delevel()) for i in system]
    
    print(forbiddenChars)
    
    # with f as fob:
        # print(fob)