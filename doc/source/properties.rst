Properties
==========

:any:`Property` objects can be defined on subclasses of :any:`Dispatcher` to create
instance attributes that emit events when their values change.
Binding and unbinding works exactly the same as with events.
The callback signature is slightly different however. The first two arguments
will be:

1. The instance object that generated the event
2. The Property value

Usage
-----

.. doctest:: property_basic_dt

    >>> from pydispatch import Dispatcher, Property
    >>> class MyEmitter(Dispatcher):
    ...     name = Property()
    ...     value = Property()
    >>> class MyListener(object):
    ...     def on_name(self, instance, value, **kwargs):
    ...         print('emitter name is {}'.format(value))
    ...     def on_value(self, instance, value, **kwargs):
    ...         print('emitter value is {}'.format(value))
    >>> emitter = MyEmitter()
    >>> listener = MyListener()
    >>> # Bind to the "name" and "value" properties of emitter
    >>> emitter.bind(name=listener.on_name, value=listener.on_value)
    >>> # Set emitter.name property (triggering the on_name callback)
    >>> emitter.name = 'foo'
    emitter name is foo
    >>> # Set emitter.value (triggering the on_value callback)
    >>> emitter.value = 42
    emitter value is 42
    >>> # If the property value assigned equals the current value:
    >>> emitter.value = 42
    >>> # No event is dispatched
    >>> emitter.value = 43
    emitter value is 43


Container Properties
--------------------

:class:`dict` and :class:`list` objects are implemented as subclasses of :any:`Property`:
    * :any:`DictProperty`
    * :any:`ListProperty`

They will emit events when their contents change. Nesting is also supported,
so even the contents of a :class:`list` or :class:`dict` anywhere inside of the
structure can trigger an event.

.. doctest:: property_containers

    >>> from pydispatch import Dispatcher, ListProperty, DictProperty
    >>> class MyEmitter(Dispatcher):
    ...     values = ListProperty()
    ...     data = DictProperty()
    >>> class MyListener(object):
    ...     def on_values(self, instance, value, **kwargs):
    ...         print('emitter.values = {}'.format(value))
    ...     def on_data(self, instance, value, **kwargs):
    ...         print('emitter.data = {}'.format(value))
    >>> emitter = MyEmitter()
    >>> listener = MyListener()
    >>> emitter.bind(values=listener.on_values, data=listener.on_data)
    >>> emitter.values.append('foo')
    emitter.values = ['foo']
    >>> emitter.values.extend(['bar', 'baz'])
    emitter.values = ['foo', 'bar', 'baz']
    >>> # The property can be assigned directly
    >>> emitter.data = {'foo':'bar'}
    emitter.data = {'foo': 'bar'}
    >>> # or using item assignment
    >>> emitter.data['foo'] = 'baz'
    emitter.data = {'foo': 'baz'}
    >>> # also through the update() method
    >>> emitter.data.update({'spam':'eggs'})
    emitter.data = {'foo': 'baz', 'spam': 'eggs'}
    >>> emitter.data.clear()
    emitter.data = {}
    >>> # Create a nested dict
    >>> emitter.data['fruit'] = {'apple':'red'}
    emitter.data = {'fruit': {'apple': 'red'}}
    >>> # changes to the inner dict are propagated and dispatched
    >>> emitter.data['fruit']['banana'] = 'yellow'
    emitter.data = {'fruit': {'apple': 'red', 'banana': 'yellow'}}
