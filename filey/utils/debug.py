__all__ = 'show pop sample nopes generator tipo'.split()


from typing import Iterable, Any
import sys, os


generator = type(i for i in '')

def show(array:Iterable[Any], indentation:int=0, enum:bool=False, first:int=1, indentor:str='\t', tail=True, head=False, file=sys.stdout, sep:str=None) -> None: 
    """
    Print each element of an array. This will consume a generator.
    """
    if (wasstr:=isinstance(file,str)): file = open(file)
    print('\n', file=file) if head else None
    for i,j in enumerate(array,first):
        print(
            (
                f"{indentation*indentor}{j}",
                f"{indentation*indentor}{i}\t{j}"
            )[enum],
            sep='',
            file=file
        )
        if sep: print(sep)
    print('\n', file=file) if tail else None
    if wasstr: file.close()


def pop(arg:Any=None, file=False, silent:bool=False) -> str:
    """
    Open the folder containing a given module, or object's module
    Open current working directory if no object is given
    Open the module's file if file=True
    Return the path which is opened
    
    This will raise an attribute error whenever there is no file to which the object/module is imputed
    """
    import os
    module = type(os)
    if arg:
        if isinstance(arg, module):
            path = arg.__file__
        else:
            mstr = arg.__module__
            if (top:=mstr.split('.')[0]) in globals().keys():
                m = eval(mstr)
            else:
                t = exec(f'import {top}')
                m = eval(mstr)
            path = m.__file__
        if not file:
            path = os.path.dirname(path)
    else:
        path = os.getcwd()
    if not silent:
        os.startfile(path)
    return path


def sample(iterable:Iterable, n:int) -> tuple:
    """
    Obtains a random sample of any length from any iterable and returns it as a tuple
    Dependencies: random.randint(a,b)
    In: iterable, lengthOfDesiredSample
    Out: iterable of length(n)
    """
    import random as r
    iterable = tuple(iterable) if type(iterable)==type({0,1}) else iterable
    choiceIndices = tuple(r.randint(0,len(iterable)-1) for i in range(n))
    return tuple(iterable[i] for i in choiceIndices)


def nopes(iterable:Iterable[Any], yeps:bool=False) -> generator:
    """
    if yeps==False
        Return the indices of all false-like boolean values of an iterable
    Return indices of all true-like boolean values of an iterable
    dependencies: None
        example
            t = (0,1,0,0,1)
            >>> tuple(nopes(t))
            (0,2,3)
            >>> tuple(nopes(t,True))
            (1,4)
    """
    for i, j in enumerate(iterable):
        if (not j, j)[yeps]:
            yield i


def tipo(inpt:Any=type(lambda:0)) -> str:
    """
    Return the name of an object's type
    Dependencies: None
    In: object
    Out: str
    """
    return str(type(inpt)).split("'")[1].split('.')[-1]