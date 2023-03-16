from importlib.metadata import version
from typing import final

__version__ = version(__name__)

__all__ = ['Container', 'NullableContainer', 'TrackingContainer']

KEY_ERROR = 'Access to key %s is currently forbidden'


class Container(dict):
    ''' Container class to hold any data.
        Acts like a class and a dictionary;
        access members with either the . notation or the [] notation
        by subclassing dict and is jsonizable without a special encoder.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This makes our dict also dottable like a class by using
        # the overt `dict` (i.e. `self`) as the storage for dottable attributes,
        # in place of the default dict CPython normally assigns to `__dict__`.
        self.__dict__ = self

    # The __repr__ supports subclassing Container, e.g. in XMLParser.py's XMLBase.
    def __repr__(self):
        return f'{type(self).__name__}({ {k: v for k, v in self.items()} })'

    # unpickling essentially does super().__init__(**state) for us, so only thing left to initialize is self.__dict__
    def __setstate__(self, state):
        self.__dict__ = self


class NullObject(object):
    def __repr__(self):
        return ''

    def __getitem__(self, attr):
        return self

    def __getattr__(self, attr):
        return self

    def __setattr__(self, attr, value):
        raise NotImplementedError('Cannot set an attribute of Undefined')

    def __bool__(self):
        return False


Undefined = NullObject()


class NullableContainer(Container):
    def __getattr__(self, attr):
        if attr.startswith('__') and attr.endswith('__'):
            return getattr(super(), attr)
        return Undefined

    def __getitem__(self, attr):
        if val := self.get(attr):
            return val
        return Undefined


@final
class TrackingContainer(dict):
    ''' A dictionary-like class that controls and logs access to its members.
        A final class not designed to be subclassed.
        Uses `__slots__ to keep the 3 <xyz>Keys attributes separate from user members.
    '''
    __slots__ = ('modifiableKeys', 'modifiedKeys', 'accessibleKeys', '__dict__', '__weakref__')

    def __init__(self, *args, modifiableKeys=None, modifiedKeys=None, accessibleKeys=None, **kwargs):  # NOSONAR legacy
        super().__init__(*args, **kwargs)

        self.__dict__ = self

        self.modifiableKeys = modifiableKeys
        self.modifiedKeys = set() if modifiedKeys is None else modifiedKeys
        self.accessibleKeys = accessibleKeys

    def __repr__(self):
        return f'{type(self).__name__}({ {k: v for k, v in self.items()} })'

    def SetAllowedAccesses(self, modifiableKeys, accessibleKeys):  # NOSONAR legacy
        ''' Change which keys a user may modify or access.

        Args:
            modifiableKeys (set):
            accesibleKeys (set):
        '''
        self.modifiableKeys = modifiableKeys
        self.modifiedKeys.clear()
        self.accessibleKeys = accessibleKeys

    def NotifyChanged(self, key):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            self.modifiedKeys.add(key)
            return super().__getitem__(key)
        else:
            raise KeyError('Assignment to key %s is currently forbidden' % key)

    def __getattr__(self, key):
        if self.accessibleKeys is None or key in self.accessibleKeys:
            try:
                return super().__getitem__(key)
            except KeyError:
                raise AttributeError()
        else:
            raise AttributeError('Access to attribute %s is currently forbidden' % key)

    def __setattr__(self, key, value):
        if key in self.__slots__:
            super().__setattr__(key, value)
        elif self.modifiableKeys is None or key in self.modifiableKeys:
            self.modifiedKeys.add(key)
            super().__setattr__(key, value)
        else:
            raise AttributeError('Assignment to attribute %s is currently forbidden' % key)

    def __getitem__(self, key):
        if self.accessibleKeys is None or key in self.accessibleKeys:
            return super().__getitem__(key)
        else:
            raise KeyError(KEY_ERROR % key)

    def __setitem__(self, key, value):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            self.modifiedKeys.add(key)
            super().__setitem__(key, value)
        else:
            raise KeyError('Assignment to key %s is currently forbidden' % key)

    def __delitem__(self, key):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            self.modifiedKeys.add(key)
            super().__delitem__(key)
        else:
            raise KeyError('Removal of key %s is currently forbidden' % key)

    def get(self, key, default=None):
        if self.accessibleKeys is None or key in self.accessibleKeys:
            return super().get(key, default)
        else:
            raise KeyError(KEY_ERROR % key)

    def __contains__(self, key):
        if self.accessibleKeys is None or key in self.accessibleKeys:
            return super().__contains__(key)
        else:
            raise KeyError(KEY_ERROR % key)

    def keys(self):
        if self.accessibleKeys is None:
            return super().keys()
        return self.accessibleKeys.intersection(super().keys())

    def pop(self, key, *args):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            self.modifiedKeys.add(key)
            return super().pop(key, *args)
        else:
            raise KeyError('Removal of key %s is currently forbidden' % key)

    def popitem(self):
        if self.modifiableKeys is None:
            return super().popitem()
        else:
            raise RuntimeError('popitem is currently forbidden')

    def clear(self):
        super().clear()
        self.SetAllowedAccesses(None, None)

    def update(self, other, /, **kwds):
        keys = set(other)
        if self.modifiableKeys is None or keys <= self.modifiableKeys:
            self.modifiedKeys |= keys
            super().update(other, **kwds)
        else:
            raise KeyError(
                'Assignment to keys in %s is currently forbidden'
                % (keys - self.modifiableKeys)
            )

    def copy(self):
        return type(self)(**self.__getstate__(), **self)

    # NOTE: this saves the user dict members
    def __reduce__(self):
        return super().__reduce__()

    # save the special attributes
    def __getstate__(self):
        return {'modifiableKeys': self.modifiableKeys,
                'modifiedKeys': self.modifiedKeys,
                'accessibleKeys': self.accessibleKeys}

    # restore the special attributes
    def __setstate__(self, state):
        # re-use __init__ for initialization
        self.__init__(**state)
