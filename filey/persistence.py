from typing import Any, Tuple
import os, pickle, re

import dill

from sl4ng.iteration import deduplicate, dictate, flat
from sl4ng.debug import tryimport, tipo

from .shell import namespacer


def dillsave(obj: Any, filename: str, overwrite: bool = True) -> Any:
    """
    Pickles the given object to a file with the given path/name.
    If the object cannot be serialized with pickle, we shall use dill instead
    Returns the object
    """
    if overwrite:
        with open(filename, 'wb') as fob:
            dill.dump(obj, fob, protocol=dill.HIGHEST_PROTOCOL)
    else:
        with open(namespacer(filename), 'wb') as fob:
            dill.dump(obj, fob, protocol=dill.HIGHEST_PROTOCOL)


def save(obj: Any, filename: str, overwrite: bool = True) -> Any:
    """
    Pickles the given object to a file with the given path/name.
    If the object cannot be serialized with pickle, we shall use dill instead
    Returns the object
    """
    try:
        if overwrite:
            with open(filename, 'wb') as fob:
                pickle.dump(obj, fob, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open(namespacer(filename), 'wb') as fob:
                pickle.dump(obj, fob, protocol=pickle.HIGHEST_PROTOCOL)
    except pickle.PicklingError:
        dillsave(obj, filename, overwrite)
    except TypeError:
        dillsave(obj, filename, overwrite)
    return obj


def load(filename: str) -> Any:
    """
    Return unpickled data from a chosen file
    If the file doesn't exist it will be created
    """

    if os.path.exists(filename):
        with open(filename, 'rb') as fob:
            var = pickle.load(fob)
            return var
    else:
        x = open(filename)
        x.close()
        return


def jar(file, duplicates: bool = False, flags: int = re.I):
    """
    Consolidate your pickles and eat them, discard the clones by default though
    """
    trash = tryimport('send2trash', 'send2trash', 'remove', 'os')
    name, ext = os.path.splitext(file)
    pattern = f'^{name}|{name}_\d+\.{ext}$'
    p = re.compile(pattern)
    folder = None if not os.sep in file else os.path.split(file)[0]
    os.chdir(folder) if folder else None
    matches = deduplicate(
        {f: load(f) for f in os.listdir(folder) if p.search(f, flags)}
    )
    results = list(matches.values())[:]
    for i in matches:
        print(i)
    [trash(file) for file in matches]
    save(results, file)


class LoggerLengthError(Exception):
    """
    A logger has reached it's maximum length
    """


class LoggerMaxLengthError(Exception):
    """
    Cannot positively update due to inevitable length error
    """


class LoggerKindError(Exception):
    """
    Tried to add an element of the wrong type
    """


class LoggerArgumentError(Exception):
    """
    Couldn't unite loggers because they have distinct arguments
    """


class LoggerAgreementError(Exception):
    """
    Shouldn't compare loggers because they have distinct arguments
    """


class Logger:
    def __init__(
        self,
        path: str = 'log.pkl',
        tight: bool = True,
        kind: [type, Tuple[type]] = None,
        max_len: int = None,
        dodge: bool = True,
    ):
        """
        Keep track of things so that you can pick up where you left off at the last runtime.
        All saves are made at the end of an update


        params
            path
                path to the logger's pickle file
            tight
                True -> no element can be added twice
            kind
                guarantees that any elements added will be of the desired type. Leave as None if you don't care
            max_len
                if the Logger's length >= max_len, the first element will be removed
            doge
                if false and IF there already exists a logger with equal arguments but different content, it's content will be synchronized and it will be overwritten upon updating.
                if true, a new name will be generated for the serial-file.
        """
        kind = (
            kind
            if isinstance(kind, (tuple, list))
            else tuple(flat([kind]))
            if kind
            else None
        )
        if os.path.exists(path):
            if isinstance((slf := load(path)), type(self)):
                omittables = '_Logger__index _Logger__itr path content'.split()
                # kws = dictate(slf.__dict__, omittables)
                kwargs = dict(zip(('tight', 'kind', 'max_len'), (tight, kind, max_len)))
                # if all(slf.__dict__.get(i)==kwargs.get(i) for i in kws):
                kws = {key: slf.__dict__[key] for key in kwargs}
                # print([j==kwargs.get(i) for i, j in kws.values()])
                # if all(j==kwargs.get(i) for i, j in kws.values()):
                if all(j == kwargs.get(i) for i, j in kws.items()):
                    self.max_len = slf.max_len
                    self.kind = slf.kind
                    self.tight = slf.tight
                    self.path = slf.path
                    self.content = slf.content
                else:
                    # diff = {key: False for key in slf.__dict__ if (val:=slf.__dict__[key])!=kwargs.get(key)}
                    # diff = {key: kws[key]==val for key, val in kwargs.items()}
                    diff = {
                        key: (kws[key], val)
                        for key, val in kwargs.items()
                        if kws[key] != val
                    }
                    # raise LoggerArgumentError(f"There is already a {tipo(self)} at the given path whose attributes do not agree:\n\t{load(path).__dict__}\n\t{kwargs}")
                    raise LoggerArgumentError(
                        f"There is already a {tipo(self)} at the given path whose"
                        f" attributes do not agree:\n\t{diff}"
                    )
            else:
                raise TypeError(
                    'There is already persistent data in a file at the given path but'
                    f' it is not an instance of the {tipo(self)!r} class'
                )
        else:
            self.max_len = max_len
            self.kind = kind
            self.tight = tight
            self.path = path
            self.content = []
        if dodge:
            self.path = namespacer(path)
        self.__index = -1

    def __repr__(self):
        r = f"Logger(length={len(self)}, tight={self.tight}, max_len={self.max_len})"
        r += f"[{', '.join(map(tipo, self.kind))}]" if self.kind else ''
        return r

    def compare(self, other):
        """
        Return essentialized versions of self's and other's __dict__ attributes
        """
        if isinstance(other, type(self)):
            omittables = '_Logger__index _Logger__itr path content'.split()
            sd = dictate(self.__dict__, omittables)
            od = dictate(other.__dict__, omittables)
            return sd, od
        raise TypeError(f"Other is not an instance of the {tipo(self)} class")

    def agree(self, other):
        """
        Check if they are suitable for concatenation
        """
        sd, od = self.compare(other)
        return sd == od

    def __eq__(self, other):
        """
        Not order sensitive
        """
        if self.agree(other):
            return sorted(self.content) == sorted(other.content)
        raise LoggerAgreementError(f"self does not agree with other")

    def __gt__(self, other):
        if self.agree(other):
            return all(i in self for i in other) and len(self) > len(other)
        raise LoggerAgreementError(f"self does not agree with other")

    def __lt__(self, other):
        if self.agree(other):
            return all(i in other for i in self) and len(self) < len(other)
        raise LoggerAgreementError(f"self does not agree with other")

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __add__(self, other):
        if self.agree(other):
            if isinstance(self.max_len, None):
                [*map(self.update, other.content)]
            elif len(other) <= self.max_len - len(self):
                [*map(self.update, other.content)]
            else:
                raise LoggerMaxLengthError(
                    'Cannot update "self" with content from "other" because the'
                    f' outcome would have more than {self.max_lengh} elements'
                )

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        self.__itr = iter(self.content)
        return self.__itr

    def __next__(self):
        if self.__index < len(self) - 1:
            self.__index += 1
            return self.content[self.__index]
        self.__index = -1
        raise StopIteration

    def __in__(self, item):
        return item in self.content

    @property
    def exists(self):
        return os.path.exists(self.path)

    def update(self, element, remove: bool = False):
        """
        Safely add/remove an element to/from, serialize, and return, self.
        """
        if remove:
            self.content.remove(element)
        else:
            if not isinstance(self.kind, type(None)):
                if not type(element) in self.kind:
                    raise LoggerKindError(f'Argument is not {self.kind}')
            if self.tight:
                if element in self:
                    return self
            if not isinstance(self.max_len, type(None)):
                if self.max_len == len(self):
                    raise LoggerLengthError("Logger has reached maximum capacity")
            self.content.append(element)
        save(self, self.path)
        return self
