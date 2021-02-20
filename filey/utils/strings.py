__all__ = "trim normalize hasdirs likefile multisplit forbiddens nameSpacer".split()

from typing import Iterable
import os, re

from .debug import *


forbiddens = r'\/:?*<>|"'

def trim(path:str, edge:str=os.sep) -> str:
    """
    Remove trailing/leading separators (or edges) from a path string
    """
    out = path[:]
    while any(out.startswith(x) for x in (edge,' ')):
        out = out[1:]
    while any(out.endswith(x) for x in (edge,' ')):
        out = out[:-1]
    return out


def normalize(path:str, relative:bool=False, force:bool=False) -> str:
    """
    Standardize a path for a current operating system.
    Given an equivalently structured file/project system, this should make code reusable across platforms 
    If force is true, all forbidden characters will be replaced with an empty string
    """
    other = ''.join(i for i in '\/' if not i==os.sep)
    if force:
        new = ''.join(i for i in path if not i in forbiddens)
    else:
        new = path[:]
    if other in path:
        terms = []
        for term in path.split(os.sep):
            if other in term:
                for part in term.split(other):
                    terms.append(part)
            else:
                terms.append(term)
        new = os.path.join(*terms)
    if relative:
        new = '.'+os.sep+path
    return new


def hasdirs(path:str) -> bool:
    """
    check if a path string contains directories or not
    """
    return bool(re.search(re.escape(os.sep), normalize(path)))


def likefile(path:str) -> bool:
    """
    Check if a path string looks like a file or not
    """
    path = normalize(path)
    return bool(re.search('readme$|.+\.(\S)+$',path.split(os.sep)[-1], re.I))


def multisplit(splitters:Iterable[str], target:str='abc') -> generator:
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


def nameSpacer(path:str, sep:str='_') -> str:
    """
    Returns a unique version of a given string by appending an integer
    Dependencies: os module
    In: string
    Out: string
    """
    id = 2
    oldPath = path[:]
    while os.path.exists(path): ##for general use
        newPath = list(os.path.splitext(path))
        if sep in newPath[0]:
            if newPath[0].split(sep)[-1].isnumeric():
                # print('case1a')
                id = newPath[0].split(sep)[-1]
                newPath[0] = newPath[0].replace(f'{sep}{id}', f'{sep}{str(int(id)+1)}')
                path = ''.join(newPath)
            else:
                # print('case1b')
                newPath[0] += f'{sep}{id}'
                path = ''.join(newPath)
                id += 1
        else:
            # print('case2')
            newPath[0] += f'{sep}{id}'
            path = ''.join(newPath)
            id += 1
    return path

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
    tests = [(eval(f'{f}(r"{p}")'), f, p) for f in __all__ for p in testPaths]
    
    show(tests)
    # show(zip(map(type, map(lambda x: Address(x).obj, testPaths)), testPaths))
    # show(zip(testPaths, map(normalize, testPaths)))
    # show(zip(testPaths, map(hasdirs, testPaths)))
    # show(zip(testPaths, map(likefile, testPaths)))