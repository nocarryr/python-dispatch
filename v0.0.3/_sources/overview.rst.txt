Overview
========

Dispatcher
----------

`Dispatcher`_ is the core component of the framework.
Subclassing this enables all of the event functionality.

Usage::

    from pydispatch import Dispatcher

    class MyEmitter(Dispatcher):
        _events_ = ['on_state', 'new_data']
        def do_some_stuff(self):
            # do stuff that makes new data
            data = self.get_some_data()
            self.emit('new_data', data=data)

    # An observer - could inherit from Dispatcher or any other class
    class MyListener(object):
        def on_new_data(self, *args, **kwargs):
            data = kwargs.get('data')
            print('I got data: {}'.format(data))
        def on_emitter_state(self, *args, **kwargs):
            print('emitter state changed')

    emitter = MyEmitter()
    listener = MyListener()

    emitter.bind(on_state=listener.on_emitter_state)
    emitter.bind(new_data=listener.on_new_data)

    emitter.do_some_stuff()
    # >>> I got data: ...

    emitter.emit('on_state')
    # >>> emitter state changed


The ``bind`` method above could also be combined::

    emitter.bind(on_state=listener.on_emitter_state,
                 new_data=listener.on_new_data)

Events can also be created after object creation::

    emitter.register_event('need_data')

    # Multiple events can also be created:
    emitter.register_event('value_changed', 'something_happened')

Stop listening by calling ``unbind``::

    emitter.unbind(listener.on_emitter_state)

    # Or to unbind all events, just supply the instance object:
    emitter.unbind(listener)

Event propagation will stop if any callback returns ``False``. Any other return
value is ignored.

There are no restrictions on event names. The idea is to keep things as simple
and non-restrictive as possible. When calling ``emit``, and positional or keyword
arguments supplied will be passed along to listeners.

.. note::

    The `Dispatcher`_ class does not use ``__init__`` for any
    of its functionality. This is again to keep things simple and get the
    framework out of your way.
    It uses ``__new__`` to handle instance creation. If your subclasses use
    ``__new__`` for something, the call to ``super()`` is required,
    but you should probably check the code to determine how it fits with your own.

Properties
----------

`Property`_ objects can be defined on subclasses of `Dispatcher`_ to create
instance attributes that emit events when their values change.
Binding and unbinding works exactly the same as with events.
The callback signature is slightly different however. The first two arguments
will be:

1. The instance object that generated the event
2. The Property value

Usage::

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

``dict`` and ``list`` objects are implemented as subclasses of ``Property``:
    * `DictProperty`_
    * `ListProperty`_

They will emit events when their contents change. Nesting is also supported,
so even the contents of a ``list`` or ``dict`` anywhere inside of the structure
can trigger an event.

Usage::

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

.. _Dispatcher: api.html#pydispatch.dispatch.Dispatcher
.. _Property: api.html#pydispatch.properties.Property
.. _ListProperty: api.html#pydispatch.properties.ListProperty
.. _DictProperty: api.html#pydispatch.properties.DictProperty
