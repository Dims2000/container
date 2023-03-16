class Container:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def clear(self):
        self.__dict__.clear()

    def copy(self):
        return Container(**self.__dict__)

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def iteritems(self):
        return self.__dict__.iteritems()

    def iterkeys(self):
        return self.__dict__.iterkeys()

    def itervalues(self):
        return self.__dict__.itervalues()

    def values(self):
        return self.__dict__.values()

    def has_key(self, key):
        return key in self.__dict__

    def update(self, dict):
        self.__dict__.update(dict)

    def get(self, key, failobj=None):
        if key not in self:
            return failobj
        return self[key]

    def setdefault(self, key, failobj=None):
        if key not in self:
            self[key] = failobj
        return self[key]

    def pop(self, key, *args):
        return self.__dict__.pop(key, *args)

    def popitem(self):
        return self.__dict__.popitem()

    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d
    fromkeys = classmethod(fromkeys)


class TrackingContainer(Container):
    """A dictionary-like class that controls and logs access to its members"""

    modifiableKeys = None
    accessibleKeys = None

    def __init__(self, **kwargs):
        """Create storage for the set of modified keys
        as a set local to this class instance.
        Call the base class's constructor"""
        Container.__init__(self, **kwargs)
        self.modifiedKeys = set()

    def SetAllowedAccesses(self, modifiableKeys, accessibleKeys):  # NOSONAR
        """Change which keys a user may modify or access.

        Args:
            modifiableKeys (set):
            accesibleKeys (set):
        """
        # set these items in such a way as to avoid __setattr__ getting called - otherwise we either end up having to
        #  allow assignement to them and/or having to avoid logging their assignment
        self.__dict__['accessibleKeys'] = accessibleKeys
        self.__dict__['modifiableKeys'] = modifiableKeys
        self.modifiedKeys.clear()

    def NotifyChanged(self, key):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            self.modifiedKeys.add(key)
            return self.__dict__[key]
        else:
            raise KeyError("Assignment to key %s is currently forbidden" % key)

    def __setitem__(self, key, value):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            self.__dict__[key] = value
            self.modifiedKeys.add(key)
        else:
            raise KeyError("Assignment to key %s is currently forbidden" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, key):
        if self.accessibleKeys is None or key in self.accessibleKeys:
            return self.__dict__[key]
        else:
            raise KeyError("Access to key %s is currently forbidden" % key)

    def __getattr__(self, key):
        return self[key]

    def keys(self):
        if self.accessibleKeys is None:
            return self.__dict__.keys()
        return self.accessibleKeys.intersection(self.__dict__.keys())

    def pop(self, key, *args):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            return self.__dict__.pop(key, *args)
        else:
            raise KeyError("Removal of key %s is currently forbidden" % key)

    def popitem(self):
        if self.modifiableKeys is None:
            return self.__dict__.popitem()
        else:
            raise RuntimeError("popitem is currently forbidden")

    def update(self, dict):
        keys = set(dict)
        if self.modifiableKeys is None or keys <= self.modifiableKeys:
            self.__dict__.update(dict)
            self.modifiedKeys |= keys
        else:
            raise KeyError("Assignment to keys in %s is currently forbidden" % (keys - self.modifiableKeys))

    def __delitem__(self, key):
        if self.modifiableKeys is None or key in self.modifiableKeys:
            del self.__dict__[key]
            self.modifiedKeys.add(key)
        else:
            raise KeyError("Removal of key %s is currently forbidden" % key)

    def __delattr__(self, key):
        del self[key]


def main():
    c = Container()
    c.foo = 17
    print(c)

    tc = TrackingContainer(test=1)
    tc.SetAllowedAccesses({'checklistDefinitions'}, {'checklistDefinitions'})
    print(tc.test)


if __name__ == '__main__':
    main()
