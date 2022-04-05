Dispatcher
==========

:any:`Dispatcher` is the core component of the framework.
Subclassing this enables all of the event functionality.

Usage
-----

.. doctest:: dispatcher_basic

    >>> from pydispatch import Dispatcher
    >>> class MyEmitter(Dispatcher):
    ...     _events_ = ['on_state', 'new_data']
    >>> # An observer - could inherit from Dispatcher or any other class
    >>> class MyListener(object):
    ...     def on_new_data(self, *args, **kwargs):
    ...         data = kwargs.get('data')
    ...         print('I got data: {}'.format(data))
    ...     def on_emitter_state(self, *args, **kwargs):
    ...         print('emitter state changed')
    >>> emitter = MyEmitter()
    >>> listener = MyListener()
    >>> emitter.bind(on_state=listener.on_emitter_state)
    >>> emitter.bind(new_data=listener.on_new_data)
    >>> emitter.emit('new_data', data='foo')
    I got data: foo
    >>> emitter.emit('on_state')
    emitter state changed


The :any:`bind <Dispatcher.bind>` method above could also be combined::

    emitter.bind(on_state=listener.on_emitter_state,
                 new_data=listener.on_new_data)

:any:`Events <Event>` can also be created after object creation::

    emitter.register_event('need_data')

    # Multiple events can also be created:
    emitter.register_event('value_changed', 'something_happened')

Stop listening by calling :any:`unbind <Dispatcher.unbind>`::

    emitter.unbind(listener.on_emitter_state)

    # Or to unbind all events, just supply the instance object:
    emitter.unbind(listener)

Callback Return Values
----------------------

Event propagation will stop if any callback returns :obj:`False`. Any other
return value is ignored.

Event Names
-----------

There are no restrictions on event names. The idea is to keep things as simple
and non-restrictive as possible. When calling :any:`emit <Dispatcher.emit>`, and
positional or keyword arguments supplied will be passed along to listeners.

Subclasses and ``__init__``
---------------------------

The :any:`Dispatcher` class does not use ``__init__`` for any
of its functionality. This is again to keep things simple and get the
framework out of your way.
It uses ``__new__`` to handle instance creation. If your subclasses use
``__new__`` for something, the call to ``super()`` is required,
but you should probably check the code to determine how it fits with your own.
