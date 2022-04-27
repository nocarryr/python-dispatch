from typing import List, Dict, Any
from pydispatch import Dispatcher, Property, ListProperty, DictProperty

class Bar(Dispatcher):
    """Summary line.
    """

    # This will not include any specific type information
    prop_a = ListProperty()
    """Description of prop_a
    """

    # This will include type information
    prop_b: List[int] = ListProperty()
    """Description of prop_b
    """

    # This will include type information and a default value
    prop_c: Dict[str, Any] = DictProperty({'foo': 'bar'})
    """Description of prop_c
    """
