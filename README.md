# python-dispatch
Lightweight event handling for Python

[![Build Status](https://travis-ci.org/nocarryr/python-dispatch.svg?branch=master)](https://travis-ci.org/nocarryr/python-dispatch)[![Coverage Status](https://coveralls.io/repos/github/nocarryr/python-dispatch/badge.svg?branch=master)](https://coveralls.io/github/nocarryr/python-dispatch?branch=master)[![PyPI version](https://badge.fury.io/py/python-dispatch.svg)](https://badge.fury.io/py/python-dispatch)[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/nocarryr/python-dispatch/master/LICENSE.txt)

## Description
This is an implementation of the "Observer Pattern" with inspiration from the
[Kivy](kivy.org) framework. Many of the features though are intentionally
stripped down and more generalized. The goal is to have a simple drop-in
library with no dependencies that stays out of the programmer's way.

## Installation
```
pip install python-dispatch
```

## Links

|               |                                              |
| -------------:|:-------------------------------------------- |
| Project Home  | https://github.com/nocarryr/python-dispatch  |
| PyPI          | https://pypi.python.org/pypi/python-dispatch |
| Documentation | https://python-dispatch.readthedocs.io       |


## Usage

### Events

```python
>>> from pydispatch import Dispatcher
>>> class MyEmitter(Dispatcher):
...     # Events are defined in classes and subclasses with the '_events_' attribute
...     _events_ = ['on_state', 'new_data']
...     def do_some_stuff(self):
...         # do stuff that makes new data
...         data = {'foo':'bar'}
...         # Then emit the change with optional positional and keyword arguments
...         self.emit('new_data', data=data)
...
>>> # An observer - could inherit from Dispatcher or any other class
>>> class MyListener(object):
...     def on_new_data(self, *args, **kwargs):
...         data = kwargs.get('data')
...         print('I got data: {}'.format(data))
...     def on_emitter_state(self, *args, **kwargs):
...         print('emitter state changed')
...
>>> emitter = MyEmitter()
>>> listener = MyListener()
>>> emitter.bind(on_state=listener.on_emitter_state)
>>> emitter.bind(new_data=listener.on_new_data)
>>> emitter.do_some_stuff()
I got data: {'foo': 'bar'}
>>> emitter.emit('on_state')
emitter state changed

```

### Properties

```python
>>> from pydispatch import Dispatcher, Property
>>> class MyEmitter(Dispatcher):
...     # Property objects are defined and named at the class level.
...     # They will become instance attributes that will emit events when their values change
...     name = Property()
...     value = Property()
...
>>> class MyListener(object):
...     def on_name(self, instance, value, **kwargs):
...         print('emitter name is {}'.format(value))
...     def on_value(self, instance, value, **kwargs):
...         print('emitter value is {}'.format(value))
...
>>> emitter = MyEmitter()
>>> listener = MyListener()
>>> emitter.bind(name=listener.on_name, value=listener.on_value)
>>> emitter.name = 'foo'
emitter name is foo
>>> emitter.value = 42
emitter value is 42

```

## Contributing

Contributions are welcome!

If you want to contribute through code or documentation, please see the
[Contributing Guide](CONTRIBUTING.md) for information.

## License

This project is released under the MIT License. See the [LICENSE](LICENSE.txt) file
for more information.
