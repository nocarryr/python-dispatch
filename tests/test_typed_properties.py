import pytest

from pydispatch import *
from pydispatch.properties import (
    ValidationError, NoneNotAllowedError, InvalidTypeError, OutOfRangeError,
)

def test_string_prop():
    class A(Dispatcher):
        foo = StringProperty()
        bar = StringProperty(allownone=False)

    a = A()
    assert a.foo is None
    a.foo = '1'
    assert a.foo == '1'
    a.foo = None
    assert a.foo is None
    a.foo = '2'

    with pytest.raises(InvalidTypeError) as exc:
        a.foo = 1
    assert 'Type "int" not valid' in exc.exconly()
    assert a.foo == '2'

    a.bar = '3'
    assert a.bar == '3'

    with pytest.raises(NoneNotAllowedError) as exc:
        a.bar = None
    assert '"None" not allowed' in exc.exconly()
    assert a.bar == '3'

def test_bool_prop():
    class A(Dispatcher):
        foo = BoolProperty()
        bar = BoolProperty(default=True, allownone=True)

    a = A()
    assert a.foo is False
    assert a.bar is True

    a.foo = True
    a.bar = False
    assert a.foo is True
    assert a.bar is False

    for value, type_name in [(1, 'int'), ('a', 'str'), (object(), 'object')]:
        with pytest.raises(InvalidTypeError) as exc:
            a.foo = value
        assert f'Type "{type_name}" not valid' in exc.exconly()
        assert a.foo is True

    with pytest.raises(NoneNotAllowedError) as exc:
        a.foo = None
    assert '"None" not allowed' in exc.exconly()
    assert a.foo is True

    a.bar = None
    assert a.bar is None

def test_int_prop():
    class A(Dispatcher):
        u = IntProperty()
        v = IntProperty(min=-10)
        w = IntProperty(max=10)
        x = IntProperty(min=-10, max=10)

    a = A()

    for value, type_name in [('a', 'str'), (True, 'bool'), (object(), 'object'), (.1, 'float')]:
        with pytest.raises(InvalidTypeError) as exc:
            a.u = value
        assert f'Type "{type_name}" not valid' in exc.exconly()

    for i in range(10):
        a.x = i
        a.x = -i

    with pytest.raises(OutOfRangeError) as exc:
        a.x = -11
    range_str = '-10 <= value <= 10'
    assert f'Value -11 must be in range "{range_str}"' in exc.exconly()

def test_float_prop():
    class A(Dispatcher):
        x = FloatProperty(min=-10, max=10)

    a = A()
    for value, type_name in [('a', 'str'), (True, 'bool'), (object(), 'object')]:
        with pytest.raises(InvalidTypeError) as exc:
            a.x = value
        assert f'Type "{type_name}" not valid' in exc.exconly()

    for i in range(10):
        a.x = i
        a.x = float(i)
        a.x = -i
        a.x = float(-i)

    range_str = '-10 <= value <= 10'
    for value in [-11, 11, -10.1, 10.1]:
        with pytest.raises(OutOfRangeError) as exc:
            a.x = value
        fvalue = float(value)
        assert f'Value {fvalue} must be in range "{range_str}"' in exc.exconly()
