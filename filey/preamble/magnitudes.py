"""
Compute the correct order of magnitude of an integer in a given dimension
"""
all = [
    'represent',
    'force',
]


from dataclasses import dataclass

# from m3ta import sample,show,nopes
from sl4ng import sample,nopes


orders = {
    0:'mono',
    1:'deca',
    2:'hecto',
    3:'kilo',
    6:'mega',
    9:'giga',
    12:'tera',
    15:'peta',
    18:'exa',
    21:'zetta',
    24:'yotta',
}

sredro = {v:k for k,v in orders.items()}

pretty = lambda number,unit='': f'{number:,} {unit}'.strip()
setcase = lambda unit,lower=False: [unit.upper().strip(),unit.lower().strip()][lower]
setlength = lambda mag,dim,long=False,sep='-': ('',sep)[long].join(((mag[0],dim[0]),(mag,dim))[long])

# def getmagnitude(value,never='mono deca hecto'.split()):
    # mags = tuple(sorted(i for i in orders.keys() if not orders[i] in never))
    # booly = lambda i: len(str(int(value))) < len(str(10**mags[i+1]))
    # fits = tuple(nopes((booly(i) for i in range(len(mags)-1)),True))
    # fit = mags[min(fits) if fits else len(mags)-1]
    # return orders[fit]

def magnitude(value,omissions='mono deca hecto'.split()):
    mags = tuple(sorted(i for i in orders.keys() if not orders[i] in omissions))
    booly = lambda i: len(str(int(value))) < len(str(10**mags[i+1]))
    fits = tuple(nopes((booly(i) for i in range(len(mags)-1)),True))
    fit = mags[min(fits) if fits else len(mags)-1]
    return orders[fit]

# def represent(self,dim='bytes',long=False,lower=False,precision=2,sep='-',omissions='mono deca hecto'.split()):
    # mag = magnitude(self,omissions)
    # unit = setcase(setlength(mag,dim,long,['',sep][long]),lower)
    # number = round(self*10**-sredro[mag],precision)
    # out = pretty(number,unit)
    # return (out.upper(),out.lower())[lower]
    

def represent(self,dim='bytes',long=False,lower=False,precision=2,sep='-',omissions='mono deca hecto'.split()):
    return force(self,mag=magnitude(self,omissions),dim=dim,long=long,lower=lower,precision=precision,sep=sep)

def force(self,mag='kilo',dim='bytes',long=False,lower=False,precision=2,sep='-'):
    # precision = sredro[mag]
    unit = setcase(setlength(mag,dim,long,sep),lower)
    val = round(self*10**-(sredro[mag]),precision)
    return pretty(val,unit)

def f2(self,dim='bytes',long=False,lower=False,precision=2,sep='-',omissions='mono deca hecto'.split()):
    """
    This should behave well on int subclasses
    """
    mag = magnitude(self,omissions)
    precision = sredro[mag] if self<5 else precision
    unit = setcase(setlength(mag,dim,long,sep),lower)
    val = round(self*10**-(sredro[mag]),precision)
    return pretty(val,unit)
    

def file_size(self,dim='bytes',mag='kilo',long=False,lower=False,precision=2,sep='-',never='mono deca hecto'.split(),force=False):
    if force:
        return force(self,mag=mag,dim=dim,long=long,lower=lower,precision=precision,sep=sep)
    return rep(self,dim=dim,long=long,lower=lower,precision=precision,sep=sep,never=never)



    
if __name__ == '__main__':
    band = lambda level,base=10,shift=0,root=1: tuple(root+i+shift for i in ((level+1)*base,level*base))[::-1]
    format = lambda selection: int(''.join(str(i) for i in selection))
    
    digits = range(*band(0))
    
    l = 0
    s = 0
    b = 30
    r = 1
    x,y = band(l,b,s,r)
    # print(x,y)
    val = sample(digits,y)
    sizes = [format(val[:i][::-1]) for i in range(x,y)]
    # show(sizes)
    # sizes = [44259260028,315436]
    
    for size in sizes[::-1]:
        # print(
        string = f"""{(len(pretty(max(sizes)))-len(pretty(size)))*' '+pretty(size)}
            {size = }
            {len(str(size)) = }
            {force(size) = }
            {force(size,mag=magnitude(size)) = }
            {f2(size) = }
            {represent(size) = }
            {magnitude(size) = }
        
            
        """.splitlines()
        print(*((x.strip(),x)[i<1] for i,x in enumerate(string)),sep='\n\t',end='\n\n')
        # )
    print(pretty(sizes[-1]))
    print(band(l,s,b,r))
    print(x,y)
    print(f'{format(digits):,}')
    # print(all(rep(size)==rep2(size) for size in sizes))