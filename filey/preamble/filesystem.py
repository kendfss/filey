"""
Implementation of a rudimentary file system

TODO:
    grab the
"""

import os, sys, shutil, pathlib
from dataclasses import dataclass

import filetype as ft
from send2trash import send2trash

from sl4ng import show, delevel, gather, nameSpacer

def trim(path,edge=os.sep):
    out = path[:]
    while out.startswith(edge):
        out = out[1:]
    while out.endswith(edge):
        out = out[:-1]
    print(out)
    return out

class size(int):
    def __repr__(self):
        return f'{round(self*10**-3):,} kb'
    
class _path(str):
    

@dataclass
class address:
    """
    A systemic pointer to the location of the data associated with a file system object
    """
    # def init(self,path:str):
        # assert os.path.exists(self.path), f'"{path}" is not a valid address on this system'
        # self.path = path
    path:str
    # if path:
        # assert os.path.exists(self.path), f'"{path}" is not a valid address on this system'
    
    @property
    def exists(self):
        return os.path.exists(self.path)
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
        else:
            raise ValueError(f'"{self.path}" is not a valid address on this system')
    if exists:
        # del isfile,isdir
        ( ,  )


class directory:
    def __init__(self,path:str):
        assert address(path).isdir, f'"{path}" is not a directory'
        self.path = trim(path)
        self._ind = -1
        cntnt = (address(os.path.join(path,i)) for i in os.listdir(path))
        for i in cntnt:
            name = os.path.split(i.path)[1]
            if i.isdir:
                setattr(self,name,i.path)
            elif i.isfile:
                setattr(self,os.path.splitext(name)[0],i.path)
        
    
    @property
    def children(self):
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=address(os.path.join(str(self),i))).isdir)
    @property
    def files(self):
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=address(os.path.join(self.path,i))).isfile)
    @property
    def content(self):
        return tuple(address(os.path.join(self.path,i).obj for i in os.listdir(self.path)))
    @property
    def leaves(self):
        return tuple(self.gather())
    @property
    def leaves(self):
        return tuple(set(i.container() for i in self.gather()))
    @property
    def name(self):
        return os.path.split(self.path)[1]
    @property
    def ancestors(self):
        level = []
        p = self.path[:]
        while p != delevel(p):
            p = delevel(p)
            level.append(p)
        return tuple(directory(i) for i in level)[::-1]
    @property
    def depth(self):
        return len(self.ancestors)
    @property
    def root(self):
        return self.ancestors[0]#.split(':')[0]
    @property
    def size(self):
        # return size(sum(os.stat(file).st_size for file in self.gather()))
        return size(sum(file.size for file in self.leaves))
    @property
    def mime(self):
        # return tuple(set(match.MIME if (match:=ft.guess(file)) else 'UNKNOWN' for file in self.gather()))
        return tuple(set(file.mime for file in self.gather()))
    @property
    def kind(self):
        return tuple(set(m.split('/')[0] for m in self.mime))
    @property
    def ext(self):
        return tuple(set(f.ext for f in self.gather()))
    @property
    def siblings(self):
        return tuple(i for i in self.container() if isinstance(i,type(self)))
    @property
    def peers(self):
        return self.container().content
    @property
    def stat(self):
        """
       return os.stat(str(self)) 
        """
        return os.stat(str(self))
    
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
    def container(self,steps=1,path=False):
        return delevel(self.path,steps) if path else directory(delevel(self.path,steps))
    def heritage(self):
        print(f'\nheritage({self.name.title()})')
        ancs = list(self.ancestors)
        ancs.append(self.path)
        for i,anc in enumerate(ancs):
            print('\t'+('','.'*i)[i>0]+i*'  '+[i for i in str(anc).split(os.sep) if i][-1])
    
    def show(self, indentation:int=1, enum:bool=False, start:int=1, indentor:str='\t'):
        assert indentation>0, f'"{indentation}" is not a viable indentation level'
        print((indentation-1)*'\t'+self.name)
        show(self.content,indentation,enum,start,indentor)
    def gather(self,names:bool=False,walk:bool=True,ext:str=None,paths=False):
        if paths:
            yield from gather(str(self),names,walk,ext)
        else:
            for path in gather(str(self),names,walk,ext):
                yield file(path)
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
    
    def isroot(self):
        return not self.depth
    def __bool__(self):
        return len(os.listdir(self.path))>0
    def __str__(self):
        return self.path
    def __repr__(self):
        return str(self)
    def __iter__(self):
        return self
    def __len__(self):
        return len(self.content)
    def __next__(self):
        if self._ind<len(self)-1:
            self._ind += 1
            return self.content[self._ind]
        self._ind = -1
        raise StopIteration
    def __getitem__(self,item):
        if item in self.content:
            return address(os.path.join(self.path,item)).obj
        raise ValueError(f'The folder "{self.name}" does not contain anything called "{item}"')
    
    move = rename
    extension = ext
    copy = clone

class file:
    def __init__(self,path:str):
        assert address(path).isfile, f'"{path}" is not a file'
        self.path = trim(path)
    
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
        return tuple(directory(i) for i in level)[::-1]
    @property
    def depth(self):
        return len(self.ancestors)
    @property
    def root(self):
        return self.ancestors[0]#.split(':')[0]
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
    @property
    def siblings(self):
        return tuple(i for i in self.container() if isinstance(i,type(self)))
    @property
    def peers(self):
        return self.container().content
    @property
    def stat(self):
        """
       return os.stat(str(self)) 
        """
        return os.stat(str(self))
    
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
    def container(self,steps=1,path=False):
        return delevel(self.path,steps) if path else directory(delevel(self.path,steps))
    def heritage(self):
        print(f'\nheritage({self.name.title()})')
        ancs = list(self.ancestors)
        ancs.append(self.path)
        for i,anc in enumerate(ancs):
            print('\t'+('','.'*i)[i>0]+i*'  '+[i for i in str(anc).split(os.sep) if i][-1])
    
    def __str__(self):
        return self.path
    def __repr__(self):
        return str(self)
        
    move = rename
    extension = ext
    copy = clone
      
if __name__ == '__main__':
    dp = r'c:\users\kenneth\videos'
    # print(directory(dp))
    # show(directory(dp).fils,)
    fp = r'c:\users\kenneth\pyo_rec.wav'
    # print(os.path.isfile(fp))
    # print(file(fp))
    fp = r'C:\Users\Kenneth\Music\Collection\slowthai\The Bottom _ North Nights\02 North Nights.mp3'
    dp = delevel(fp,1)
    
    d = address(dp).obj
    print(d)
    # d.show(1)
    f = address(fp).obj
    print(f)
    
    system = (d,f)
    print(system)
    print([i.name for i in system])
    print([i.depth for i in system])
    print([i.ancestors for i in system])
    print([i.heritage() for i in system])
    print([i.root for i in system])
    print([i.size for i in system])
    [print(i.size) for i in system]
    [print(i.kind) for i in system]
    [print(i.ext) for i in system]
    [print(i.stat) for i in system]
    print(d.leaves)
    
    # d.moveContent(r'c:\users\kenneth\downloads\\')
    # print(f.clone(touch=True))
    # print(f.clone())
    # print(f.move(nameSpacer(str(f))))
    # os.startfile(f.container().path)
    # help(f)
    # for i in d:
        # ob = d[i]
        # print(ob,ob.kind,ob.ext)
        # if isinstance(ob,directory):
            # for o in ob.children:
                # o2 = ob[o]
                # print('\t',o2,o2.kind,o2.ext)
    
    # for p in d.gather():
        # print(p.size,p.mime,p.ext,sys.getrefcount(p))
        # f = file(p)
        # if 'matroska' in f.mime:
            # print(f.container())
            # print(f.name)
            # print(f.size)
            
            
    # for i in d:print(i)
    # print(os.stat(dp).st_size)
    # print(os.stat(fp).st_size)
    # print(dict(d))
    # d.heritage()
    # os.rename('Few Nolder','randombumbashit')
    # print(os.listdir('randombumbashit'))