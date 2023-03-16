import pickle
from importlib.metadata import version

import pytest

import container
from container import Container, NullableContainer, NullObject, TrackingContainer


def test_version():
    package_version = version('container')
    assert container.__version__ == package_version


def test_dot():
    c = Container(k=17)
    assert c.k == c['k']


def test_repr():
    c = Container(k=17)
    assert repr(c) == "Container({'k': 17})"


def test_pickle():
    c = Container(k=17)
    dill = pickle.dumps(c)
    c1 = pickle.loads(dill)
    assert c == c1


def test_nullable():
    n = NullableContainer({'k1': 1, 'k2': NullableContainer({'nk1': 'fred'})})
    assert repr(n.foo) == ''  # repr
    assert isinstance(n.foo.bar, NullObject)
    assert repr(n.foo.bar) == ''  # NullObject __getattr__

    with pytest.raises(NotImplementedError):  # NullObject __setattr__
        n.foo.bar = None

    assert repr(n.foo['bar']) == ''  # NullObject __getitem__
    assert not bool(n.foo)  # NullObject bool

    with pytest.raises(AttributeError):
        assert n.__name__

    assert isinstance(n['name'], NullObject)

    assert n['k1']


def test_tracking():
    tc = TrackingContainer({'test': 17})

    assert repr(tc) == "TrackingContainer({'test': 17})"

    assert tc.test

    assert tc['test'] == 17

    with pytest.raises(AttributeError):
        assert tc.testx

    tc.checklistDefinitions = {}
    tc.checklistDefinitions['a'] = None

    assert tc.modifiedKeys == {'checklistDefinitions'}

    tc['test1'] = 'z'
    del tc['test1']

    tc['test1'] = 'y'
    assert tc.pop('test1') == 'y'

    tc['test1'] = 'x'
    assert tc.popitem() == ('test1', 'x')

    tc['test1'] = 'a'

    tc.update({'test2': 't'})

    assert tc.get('test1') == 'a'

    assert 'test1' in tc

    assert list(tc.keys()) == ['test', 'checklistDefinitions', 'test1', 'test2']

    assert list(tc.values()) == [17, {'a': None}, 'a', 't']

    assert tc.copy() == tc

    tc.SetAllowedAccesses({'checklistDefinitions'}, {'checklistDefinitions', 'test'})

    with pytest.raises(AttributeError):
        tc.testx = 18

    with pytest.raises(KeyError):
        assert tc['test1']

    with pytest.raises(KeyError):
        assert tc.get('test1')

    with pytest.raises(KeyError):
        assert tc.pop('test1')

    with pytest.raises(KeyError):
        assert 'test1' in tc

    with pytest.raises(KeyError):
        assert tc.update({'test2': 't'})

    with pytest.raises(RuntimeError):
        tc.popitem()

    assert 'checklistDefinitions' in list(tc.keys())

    with pytest.raises(KeyError):
        del tc['test1']

    with pytest.raises(KeyError):
        tc['test1'] = 'b'

    tc.NotifyChanged('checklistDefinitions')
    assert tc.modifiedKeys == {'checklistDefinitions'}

    with pytest.raises(KeyError):
        tc.NotifyChanged('fred')

    # AttributeError
    with pytest.raises(AttributeError):
        assert tc.foo

    assert tc.test == 17

    dill = pickle.dumps(tc)
    tc1 = pickle.loads(dill)
    assert tc == tc1

    tc.clear()
    assert dict(tc) == {}
