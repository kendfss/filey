from pathlib import Path
from functools import reduce, cached_property
import os, re, sys, shutil


import filetype as ft
from send2trash import send2trash
import audio_metadata as am


from sl4ng import show, delevel, gather, nameSpacer, ffplay, commons, nopes
# from magnitudes import represent# as rp

def normalize(path, relative=False):
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

def hasdirs(path):
    return bool(re.search(re.escape(os.sep),normalize(path)))

def likeFile(path):
    path = normalize(path)
    return bool(re.search('readme$|.+\.(\S)+$',path.split(os.sep)[-1],re.I))



class address:
    def __init__(self, path):
        self.path = path = normalize(path)
        if not os.path.exists(path):
            print(Warning(f'Warning: Path "{path}" does not exist'))
    def __str__(self):
        return self.path
    def __repr__(self):
        return self.path
    def __hash__(self):
        return hash(self.path)
    
    def create(self, content=None, raw=False):
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
    def isdir(self):
        return os.path.isdir(self.path)
    @property
    def isfile(self):
        return os.path.isfile(self.path)
    @property
    def exists(self):
        return os.path.exists(self.path)
    @property
    def obj(self):
        if self.exists:
            return file(self.path) if self.isfile else folder(self.path)
        else:
            return file(self.path) if likeFile(self.path) else directory(self.path)
    @property
    def up(self):
        return address(delevel(self.path)).obj
    @property
    def name(self):
        return os.path.split(self.path)[1]
    
    @property
    def ancestors(self):
        """
        
        """
        level = []
        p = self.path[:]
        while p != delevel(p):
            p = delevel(p)
            level.append(p)
        return tuple(address(i).obj for i in level)[::-1]
    @property
    def colleagues(self):
        """
        
        """
        return tuple(i for i in self.up if isinstance(i, type(self)))
    @property
    def neighbours(self):
        """
        
        """
        return self.up.content
    @property
    def depth(self):
        """
        
        """
        return len(self.ancestors)
    @property
    def top(self):
        """
        
        """
        return self.ancestors[0]#.split(':')[0]
    @property
    def stat(self):
        """
       return os.stat(self.path) 
        """
        return os.stat(self.path)
        
    def delevel(self, steps=1, path=False):
        """
        
        """
        return delevel(self.path,steps) if path else directory(delevel(self.path,steps))
    def heritage(self):
        """
        
        """
        print(f'\nheritage({self.name.title()})')
        ancs = list(self.ancestors)
        ancs.append(self.path)
        for i,anc in enumerate(ancs):
            print('\t'+('','.'*i)[i>0]+i*'  '+[i for i in str(anc).split(os.sep) if i][-1])
    
    def touch(self):
        """
        
        """
        p = self.path
        pathlib.Path(p).touch()
        self = address(p).obj
        return self
    def erase(self, recycle=True):
        """
        
        """
        send2trash(self.path) if recycle else os.remove(self.path)
        return self
    def rename(self, new, relative=False):
        """
        
        """
        new = new if not relative else os.path.join(delevel(self.path),new)
        os.makedirs(delevel(new),exist_ok=True)
        os.rename(self.path,new)
        self = address(new).obj
        return self
    def clone(self,new=None, relative=False, touch=False):
        """
        
        """
        
        if new:
            if os.path.isdir(new):
                new = nameSpacer(os.path.join(new, self.name))
            if relative:
                new = nameSpacer(os.path.join(delevel(self.path), self.name))
        else:
            new = nameSpacer(os.path.join(delevel(self.path), self.name))
        os.makedirs(delevel(new), exist_ok=True)
        shutil.copy2(self.path, new)
        out = address(new).obj
        return out.touch() if touch else out
        
    def expose(self):
        """
        
        """
        os.startfile(self.path)
        return self
        
class file(address):
    @property
    def title(self):
        return os.path.splitext(self.name)[0]
    
    def content(mode='rb'):
        """
        
        """
        with open(self.path, mode) as fobj:
            return fobj
    
class directory(address):
    def __init__(self,path:str):
        path = os.path.abspath(trim(path))
        assert address(path)#.isdir, f'"{path}" is not a directory'
        super(directory,self).__init__(path)
        self._ind = -1
    def __len__(self):
        return len(self.content)
    def __bool__(self):
        """
        Check if the directory is empty or not
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
    def __getitem__(self,item):
        if any(re.search(f'^{item}$',i.name,re.I) for i in self.content):
        # for i in nopes((re.search(f'^{item}$',i.name,re.I) for i in self.content),True):
            return address(os.path.join(self.path,item)).obj
        raise ValueError(f'The folder "{self.name}" does not contain anything called "{item}"')
    
    @property
    def children(self):
        """
        Return "os.listdir" but filtered for directories
        """
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=address(os.path.join(str(self),i))).isdir)
    @property
    def files(self):
        """
        Return "os.listdir" but filtered for files
        """
        return tuple(addy.obj for i in os.listdir(self.path) if (addy:=address(os.path.join(self.path,i))).isfile)
    @property
    def content(self):
        """
        Return address-like objects from "os.listdir"
        """
        return tuple(address(os.path.join(self.path,i)).obj for i in os.listdir(self.path))
    @property
    def leaves(self):
        """
        Return All files from all branches
        """
        return tuple(self.gather())
    @property
    def branches(self):
        """
        Return Every directory whose path contains "self.path"
        """
        return tuple(set(i.delevel() for i in self.gather()))
    @property
    def size(self):
        """
        Return Prettified version of _size
        """
        return sum(file.size for file in self.leaves)
    @property
    def _size(self):
        """
        Return sum of file sizes for all leaves
        """
        return sum(file.size for file in self.leaves)
    @property
    def mimes(self):
        """
        Return file mimes for all files from all branches
        """
        return tuple(set(file.mime for file in self.gather()))
    @property
    def kinds(self):
        """
        Return file types for all files from branches
        """
        return tuple(set(m.split('/')[0] for m in self.mime))
    @property
    def exts(self):
        """
        Return extensions for all files from all branches
        """
        return tuple(set(f.ext for f in self.gather()))
    @property
    def isroot(self) -> bool:
        """
        Return check if the directory is at the highest level of the file system
        """
        return not self.depth
    
    def add(self, other, copy=False):
        """
        Introduce new elements. Send an address-like object to self.
        """
        new = os.path.join(self.path, os.path.split(other.path)[-1])
        other.rename(new)
        return self
    
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
    # show(zip(testPaths,map(normalize,testPaths)))
    # show(zip(testPaths,map(hasdirs,testPaths)))
    # show(zip(testPaths,map(likeFile,testPaths)))
    
    # ddemo = address(os.path.join(*mock[:-1])).obj
    # fdemo = address(os.path.join(*mock)).obj
    # ddemo = directory(os.path.join(*mock[:-1]))
    # fdemo = file(os.path.join(*mock))
    
    fp = r'c:\users\kenneth\pyo_rec.wav'
    dp = r'c:\users\kenneth\videos'
    
    d = directory(dp)
    f = file(fp)
    
    system = (d,f)
    