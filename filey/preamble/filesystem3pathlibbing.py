from pathlib import Path
from functools import reduce, cached_property
import os, re

from sl4ng import show


def normalize(path,relative=False):
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


class address(Path):
    def __init__(self,string):
        string = normalize(self.string)
        if not os.path.exists(string):
            print(Warning(f'Warning: Path "{string}" does not exist'))
        

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
    
    demo = address(os.path.join(*mock))