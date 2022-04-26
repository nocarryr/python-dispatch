from pydispatch import Dispatcher, Property

class Foo(Dispatcher):
    """Summary line.
    """

    # This will not include any specific type information
    prop_a = Property()
    """Description of prop_a
    """

    # This will include type information and a default value
    prop_b: int = Property(0)
    """Description of prop_b
    """
