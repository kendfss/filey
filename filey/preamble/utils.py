from sl4ng import gen, show, chords, flatten as chain
from itertools import chain, tee
from typing import Sequence

def multisplit(splitters:Sequence[str], target:str) -> gen:
    """
    Split a string by a sequence of arguments
    >>> list(multisplit(',`* ', 'wma,wmv mp3`vga*mp4 ,`*  ogg'))
    ['wma', 'wmv', 'mp3', 'vga', 'mp4', 'ogg']
    """
    result = target.split(splitters[0])
    for splitter in splitters[1:]:
        result = [*chain.from_iterable(i.split(splitter) for i in result)]
    # yield from [i for i in result if i]
    yield from filter(None,result)
        


# multisplit('a b c'.split(), 'carrot cabbage macabre'.split(','))
x, y = tee(multisplit('a b c'.split(), 'carrot cabbage macabre'))
x, y = tee(multisplit(',`* ', 'carrot cabbage macabre'))
x, y = tee(multisplit(',`* ', 'wma,wmv mp3`vga*mp4 ,`*  ogg'))
show(x)
print(list(y))