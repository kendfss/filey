from typing import Dict, List, Callable
from subprocess import run, Popen
from pathlib import Path
from time import sleep
import re, os, platform, sys

from pyperclip import copy, paste
from sl4ng import show, getsource, pop, unzip, main, join, ffplay, regenerator, kill, kbd, convert
from filey import Address, Directory, File
import sl4ng, filey

def clear():
    Popen('clear')
    sleep(.2)
def cls():
    clear()
    show(map(repr, cd), head=False, tail=False)

architecture = platform.architecture()

escaped = tuple(i for i in kbd() if re.escape(i)!=i)

this = __file__
here = os.path.dirname(__file__)

c = Directory('c:/')
e = Directory('e:/')
f = Directory('f:/')

cd = Directory('.')
user = Directory('~')
documents = user/'documents'
root = c if c.exists else None
appdata = user/'appdata'

downs = user / 'Downloads'
web = downs / 'tools/languages' # need library class

dev = Directory(r"e:/")
sp = dev / 'shellpower'

git = dev / 'gitting'
clones = git/'gitclone/clones'
ignore = clones / 'github/gitignore'
mdn = git / r'gitclone\clones\mdn\content\files\en-us'
brython = git / r'gitclone\clones\brython-dev\brython\www\doc\en'

projects = dev / 'projects'
monties = projects / 'monties'

site = dev / 'Languages\Python38-64\lib'
docs = monties / 'docs'

prod = Directory(r'f:/')
flps = prod / 'programs/project files/fl'

def killfl():
    kill('fl64')
    kill('ilbridge')

def chdir(path):
    global cd
    # import os
    os.chdir(path)
    cd = Directory(path)
# os.chdir = chdir

# p = videos / "please refrain from touching the pelican\\told you so"
# play = lambda x, d=p: ffplay((d/x).path, hide=False, loop=False, fullscreen=False)
# rename = lambda x, y, d=p: (d/x).rename(y)
# find = lambda words, ext='': show

class Scanner:
    """
    Create an object which scans a text file for a given keyword
    """
    def __init__(self, keywords:str, mode:str='r', strict:bool=True, prescaped:bool=False, casefold:bool=True, opener:Callable=open, lines:bool=True):
        """
        params:
            keywords
                terms to search for
            mode
                'r' or 'rb'
            strict
                True -> search for words 
                False -> clauses
            prescaped
                whether or not terms have already been regex escaped
            casefold
                true -> case insensitive
            opener
                must return an object with a "readlines" or "read" method  (depends on lines)
            lines
                
        """
        self.casefold = casefold
        self.keywords = keywords
        self.opener = opener
        self.lines = lines
        self.mode = mode
        self.strict = strict
        self.prescaped = prescaped
    @property
    def __keywords(self):
        """
        handles any necessary escaping
        """
        return re.escape(self.keywords) if not self.prescaped else self.keywords
    @property
    def __casefold(self):
        """
        standardize the case-fold setting
        """
        return re.I if self.casefold else 0
    @property
    def pattern(self):
        """
        compile the search pattern
        """
        return re.compile(
            (
                join(self.__keywords.split(), '|'), 
                self.__keywords
            )[self.strict], 
            self.__casefold
        )
    def __call__(self, path:str, lines:bool=None):
        """
        Scan a file at a given path for a predefined word/clause
        """
        if isinstance(lines, type(None)):
            lines = self.lines
        with self.opener(path, self.mode) as fob:
            if lines:
                return self.pattern.search(path) or any(map(self.pattern.search, fob.readlines()))
            return self.pattern.search(path) or any(map(self.pattern.search, fob.read()))
def scan(keywords:str, mode='r', strict=True, prescaped=False, casefold=True):
    casefold = (0, re.I)[casefold]
    keywords = re.escape(keywords) if not prescaped else keywords
    pattern = re.compile(keywords if strict and not prescaped else join(keywords.split(), '|'), casefold)
    def wrap(path):   
        with open(path, mode) as fob:
            return any(map(pattern.search, fob.readlines())) or pattern.search(path)
    return wrap
# show(user('', ext='txt'))

def philter(func, itr, start=1, index=False):
    for i, e in enumerate(itr, start):
        if any(j in e for j in 'venv'.split()):
                continue
        else:
            try:
                if func(e):
                    # yield i, e if index else e
                    yield (e, (i, e))[index]
            except UnicodeDecodeError:
                # print(f"UnicodeDecodeError @ {e}")
                # raise 
                # break
                continue
def docsearch(keywords:str, location:Directory=monties, ext:str='py'):
    show(filter(scan(keywords), location('', ext=ext)))
exotics = {
    "cdot": "·",
}
exords = {key: ord(val) for key, val in exotics.items()}
tfs = [
    r'C:\Users\Kenneth\childlist.txt',
    r'C:\Users\Kenneth\file.txt',
    # r'C:\Users\Kenneth\frozenpips.txt',
    r'C:\Users\Kenneth\parentlist.txt',
    # r'C:\Users\Kenneth\pipfreeze.txt',
    # r'C:\Users\Kenneth\pipsweets.txt',
]


# tword = 'def clone'
# show(filter(scan(tword), monties('', ext='py')))
# show(map(pop, filter(scan(tword), tfs)))
# show(filter(scan(tword), tfs))


# show(downs('tensor', ext='pdf'))
# with open('')
# with (Directory('~') / 'pyo_rec.wav').open('r') as fob:
    # help(fob)
    # print(fob.read())
    # fob = fob.open(
# f = (Directory('~') / 'pyo_rec.wav')
# help(f.open)
