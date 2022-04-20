import typing as tp

from pydispatch import Dispatcher
from pydispatch.properties import Property, DictProperty, ListProperty

class TheClass(Dispatcher):
    """Docstring for TheClass

    Look at :attr:`foo`, :obj:`bar` and
    :dispatcherproperty:`baz`
    """

    foo = Property(False)
    """Docstring for foo"""

    bar = DictProperty()
    """Docstring for bar"""

    baz = ListProperty()
    """Docstring for baz"""

class TheOtherClass(Dispatcher):
    """Docstring for TheOtherClass

    Look at :attr:`foo`, :obj:`bar` and
    :dispatcherproperty:`baz`
    """

    foo: int = Property(0)
    """Docstring for foo"""

    bar: tp.Dict[str, TheClass] = DictProperty()
    """Docstring for bar"""

    baz: tp.List[str] = ListProperty()
    """Docstring for baz"""
