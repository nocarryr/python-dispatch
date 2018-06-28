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

::

    from pydispatch import Dispatcher, Property

    class MyEmitter(Dispatcher):
        name = Property()
        value = Property()

    class MyListener(object):
        def on_name(self, instance, value, **kwargs):
            print('emitter name is {}'.format(value))
        def on_value(self, instance, value, **kwargs):
            print('emitter value is {}'.format(value))

    emitter = MyEmitter()
    listener = MyListener()

    emitter.bind(name=listener.on_name, value=listener.on_value)

    emitter.name = 'foo'
    # >>> emitter name is foo
    emitter.value = 42
    # >>> emitter value is 42

If the attribute is set to the same value, an event is not dispatched::

    emitter.value = 42
    # No event
    emitter.value = 43
    # >>> emitter value is 43


Container Properties
--------------------

:class:`dict` and :class:`list` objects are implemented as subclasses of :any:`Property`:
    * :any:`DictProperty`
    * :any:`ListProperty`

They will emit events when their contents change. Nesting is also supported,
so even the contents of a :class:`list` or :class:`dict` anywhere inside of the
structure can trigger an event.

::

    from pydispatch import Dispatcher
    from pydispatch.properties import ListProperty, DictProperty

    class MyEmitter(Dispatcher):
        values = ListProperty()
        data = DictProperty()

    emitter = MyEmitter()

    emitter.values.append('foo')
    print(emitter.values)
    # >>> ['foo']

    emitter.values.extend(['bar', 'baz'])
    print(emitter.values)
    # >>> ['foo', 'bar', 'baz']

    emitter.data = {'foo':'bar'}
    # or
    emitter.data['foo'] = 'bar'
    print(emitter.data)
    # >>> {'foo':'bar'}

    emitter.data['fruit'] = {'apple':'red'}
    emitter.data['fruit']['banana'] = 'yellow'
    # event would be dispatched to listeners
