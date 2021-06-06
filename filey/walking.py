# __all__ = "walk files folders".split()
__all__ = "search_iter files show search folders walk".split()


from typing import Iterator, Iterable, Any
from itertools import permutations, chain
import os, re
from sl4ng import pop, show, multisplit, join, mainame, eq

def walk(root:str='.', dirs:bool=False, absolute:bool=True) -> Iterator[str]:
    """
    Walk a directory's tree yielding paths to any files and/or folders along the way
    This will always yield files. 
    If you only want directories, look for the "folders" function in filey.utils.walkers
    
    Caution:  if you pass a relative pathname for top, don't change the
    current working directory between resumptions of walk.  walk never
    changes the current directory, and assumes that the client doesn't
    either. - taken from os.walk documentation
    
    Params
        root: str|pathlike|Place
            path to starting directory
        folders
            (True -> omit, False -> include) paths to directories
        absolute
            yield (True -> absolute paths, False -> names only)
    """
    root = (str, os.path.realpath)[absolute](str(root))
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            if dirs:
                yield (name, path)[absolute]
            yield from walk(path, dirs=dirs, absolute=absolute)
        else:
            yield (name, path)[absolute]

def parse_extensions(extensions:str) -> re.Pattern:
    """
    Create a regex parser to check for file extensions. 
        Note: Separate extensions by one of
            [',', '`', '*', ' ']
    """
    sep = [i for i in ',`* ' if i in extensions]
    pattern = '|'.join(f'\.{i}$' for i in extensions.split(sep[0] if sep else None))
    pat = re.compile(pattern, re.I)
    return pat

def files(root:str='.', exts:str='', negative:bool=False, absolute:bool=True) -> Iterator[str]:
    """
    Search for files along a directory's tree.
    Also (in/ex)-clude any whose extension satisfies the requirement
        
    Params
        root: str|pathlike|Place
            path to starting directory
        exts
            extensions of interest. 
            you can pass more than one extension at a time by separating them with one of the following:
                [',', '`', '*', ' ']
        negative
            (True -> omit, False -> include) matching extensions
        absolute
            yield (True -> abspaths, False -> names only)
    """
    root = (str, os.path.realpath)[absolute](str(root))
    pat = parse_extensions(exts)
    predicate = lambda x: not bool(pat.search(x)) if negative else bool(pat.search(x))
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            yield from files(path, exts=exts, negative=negative, absolute=absolute)
        elif predicate(path):
            yield (name, path)[absolute]

def folders(root:str='.', absolute:bool=True) -> Iterator[str]:
    """
    Search for files along a directory's tree.
    Also (in/ex)-clude any whose extension satisfies the requirement
        
    Params
        root: str|pathlike|Place
            path to starting directory
        exts
            extensions of interest. 
            you can pass more than one extension at a time by separating them with any of the following:
                [',', '`', '*', ' ']
        negative
            (True -> omit, False -> include) matching extensions
        absolute
            yield (True -> abspaths, False -> names only)
    """
    root = (str, os.path.realpath)[absolute](str(root))
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path):
            yield (name, path)[absolute]
            yield from folders(path, absolute=absolute)

def __term_perms(terms:str, case:int, tight:bool) -> re.Pattern:
    """
    compute the regex pattern for posible permutations of search terms
    """
    sep = "[\\ _\\-]*" if tight else "(.)*"
    if isinstance(terms, str):
        terms = terms.split()
    terms = map(re.escape, terms)
    rack = (sep.join(perm) for perm in permutations(terms))
    return re.compile("|".join(rack), case)


def search_iter(iterable:str, terms:Iterable[str], exts:str='', case:bool=False, negative:bool=False, dirs:int=0, strict:int=1, regex:bool=False, names:bool=True) -> Iterator[str]:
    """
    Find files matching the given terms within a directory's tree
    Params
        root
            the directory in which the walking search commences
            separate by spaces
        terms
            the terms sought after
            separate by spaces
        exts
            any file extensions you wish to check for
        case
            toggle case sensitivity
        negative
            Ignored unless dirs==0. Any files matching the terms will be omitted.
        dirs
            0 -> ignore all directories
            1 -> directories and files
            2 -> directories only
        strict
            0 -> match any terms in any order
            1 -> match all terms in any order (interruptions allowed)
            2 -> match all terms in any order (no interruptions allowed)
            3 -> match all terms in given order (interruptions)
            4 -> match all terms in given order (no interruptions)
            combinations of the following are not counted as interruptions:
                [' ', '_', '-']
            5 -> match string will be compiled as though it was preformatted regex
        names
            True -> only yield results whose names match
            False -> yield results who match at any level
    """
    tight = strict in (2, 4)
    sep = "[\\ _\\-]*" if tight else "(.)*"
    scope = (str, lambda x: os.path.split(x)[1])[names]
    case = 0 if case else re.I
    
    expat = parse_extensions(exts)
    tepat = {
        0: re.compile("|".join(map(re.escape, terms.split())), case),
        1: __term_perms(terms, case, 0),
        2: __term_perms(terms, case, 1),
        3: re.compile(sep.join(map(re.escape, terms)), case),
        4: re.compile(sep.join(map(re.escape, terms)), case),
        5: re.compile(terms, case)
    }[strict] if not regex else re.compile(terms, case)
    
    predicate = (
        lambda i: tepat.search(i) and expat.search(i),
        lambda i: not (tepat.search(i) or expat.search(i)),
    )[negative]
    
    for i in iterable:
        if predicate(scope(i)):
            yield i

def search(root:str, terms:Iterable[str], exts:str='', case:bool=False, negative:bool=False, dirs:int=0, strict:int=1, regex:bool=False, names:bool=True) -> Iterator[str]:
    """
    Find files matching the given terms within a directory's tree
    Uses linear search
    Params
        root
            the directory in which the walking search commences
            separate by spaces
        terms
            the terms sought after
        exts
            any file extensions you wish to check for
            separate by spaces
        case
            toggle case sensitivity
        negative
            Any files/folders with names or extensions matching the terms and exts will be omitted.
        dirs
            0 -> ignore all directories
            1 -> directories and files
            2 -> directories only
        strict
            0 -> match any terms in any order
            1 -> match all terms in any order (interruptions allowed)
            2 -> match all terms in any order (no interruptions allowed)
            3 -> match all terms in given order (interruptions)
            4 -> match all terms in given order (no interruptions)
            combinations of the following are not counted as interruptions:
                [' ', '_', '-']
            5 -> match string will be compiled as though it was preformatted regex
        names
            True -> only yield results whose names match
            False -> yield results who match at any level
    """
    func = {
        0: files,
        1: walk,
        2: folders,
    }[dirs]
    kwargs = {
        0: { "exts": exts, "negative": negative, "absolute": True, },
        1: { "dirs": True, "absolute": True, },
        2: { "absolute": True, },
    }[dirs]
    
    yield from search_iter(
        (i for i in func(root, **kwargs)), 
        terms=terms, exts=exts, case=case, 
        negative=negative, dirs=dirs, 
        strict=strict, names=names
    )


if __name__ == "__main__":
    folder = r'E:\Projects\Monties\2021\file management'
    folder = 'C:\\Users\\Kenneth\\Downloads\\byextension'
    folder = r"E:\Projects\Monties\2021\media\file_management\filey"
    folder = "../../.."
    folder = "c:/users/kenneth/pictures"

    # box = [*walk(folder, absolute=True)]
    # print(all(map(os.path.exists, box)))
    # print(__file__ in box)
    # show(box, 0, 1)
    
    # box = [*walk(folder, dirs=False, absolute=True)]
    # box2 = [*files(folder, exts='', absolute=True)]
    # print(all(i in box2 for i in box) and all(i in box for i in box2))
    
    # exts = 'jpg .jpeg pdf'
    # show([*files(folder, exts=exts, negative=False, absolute=True)])

    # box = [*walk(folder, dirs=False, absolute=True)]
    # box2 = [*files(folder, exts=exts, negative=False, absolute=True)]
    # box3 = [*files(folder, exts=exts, negative=True, absolute=True)]
    # print(eq(map(sorted, (box2+box3, box))))
    
    
    # box4 = [*folders(folder, True)]
    # show(box4, 0, 1)
    # show(search(folder, '__init__'))
    show(search(folder, '_', 'png'))