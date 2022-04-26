Usage
=====

This extension adds support for documenting :class:`~pydispatch.dispatch.Event`
and :class:`~pydispatch.properties.Property` objects automatically through the
:mod:`autodoc <sphinx.ext.autodoc>` extension.


Configuration
-------------

To enable this, "pydispatch_sphinx" must be included in the ``extensions`` list
of your project's ``conf.py``::

    extensions = [
        'sphinx.ext.autodoc',
        ...
        'pydispatch_sphinx',
    ]

To take full advantage of the extension, the :mod:`intersphinx <sphinx.ext.intersphinx>`
extension is recommended.

Add "sphinx.ext.intersphinx" to the ``extensions`` list::

    extensions = [
        'sphinx.ext.autodoc',
        'sphinx.ext.intersphinx',
        ...
        'pydispatch_sphinx',
    ]

And add the "python-dispatch" URL to ``intersphinx_mapping`` in ``conf.py``::

    intersphinx_mapping = {
        'pydispatch': ('https://python-dispatch.readthedocs.io/en/latest/', None),
        ...
    }


.. _documenting-properties:

Documenting Properties
----------------------

When used with the :rst:dir:`automodule` or :rst:dir:`autoclass` directive,
any :class:`~pydispatch.properties.Property` (or its subclasses) that have
docstrings will be detected and their markup will be added using the
:rst:dir:`autodispatcherproperty` directive.

If :pep:`484` type hints exist, they will be represented accordingly using the
``:type:`` option of :rst:dir:`autodispatcherproperty`. If a default value is
specified, it will also be included in the final output.

See the docstring examples below with their corresponding reStructuredText output.


Property Objects
^^^^^^^^^^^^^^^^

.. panels::

    Python Docstring
    ^^^^^^^^^^^^^^^^

    .. literalinclude:: sphinx_autodoc_examples/prop_foo.py

    ---

    HTML Output
    ^^^^^^^^^^^

    .. autoclass:: prop_foo.Foo
        :members:


Container Properties
^^^^^^^^^^^^^^^^^^^^

.. panels::

    Python Docstring
    ^^^^^^^^^^^^^^^^

    .. literalinclude:: sphinx_autodoc_examples/prop_bar.py

    ---

    HTML Ouput
    ^^^^^^^^^^

    .. autoclass:: prop_bar.Bar
        :members:


.. _documenting-events:

Documenting Events
------------------

Documenting :class:`Events <pydispatch.dispatch.Event>` is similar to
:ref:`documenting properties <documenting-properties>`, except events are not
defined individually at the class level.
See :class:`here <pydispatch.dispatch.Dispatcher>` for details.

The :rst:dir:`event` and :rst:dir:`autoevent` directives are used to
represent Events.


Attribute Annotation
^^^^^^^^^^^^^^^^^^^^

To include events in your documentation, annotations may be added to the class
body with the event name to document as the attribute and
:class:`~pydispatch.dispatch.Event` as its type.


.. panels::

    Python Docstring
    ^^^^^^^^^^^^^^^^

    .. literalinclude:: sphinx_autodoc_examples/event_baz.py

    ---

    HTML Ouput
    ^^^^^^^^^^

    .. autoclass:: event_baz.Baz
        :members:


Method Annotation
^^^^^^^^^^^^^^^^^

Another method of documenting events is to define a method with the same name
as the event. This also allows you add type hints for the event.


.. panels::

    Python Docstring
    ^^^^^^^^^^^^^^^^

    .. literalinclude:: sphinx_autodoc_examples/event_spam.py


    ---

    HTML Ouput
    ^^^^^^^^^^

    .. autoclass:: event_spam.Spam
        :members:


.. _cross-referencing:

Cross Referencing
-----------------

Property objects may be referenced by the :rst:role:`py:dispatcherproperty` role
and Events referenced by the :rst:role:`py:event` role.

Note that "property" was not chosen as a role name to avoid
conflicts with the built-in :any:`property` decorator.

For convenience though (since ``dispatcherproperty`` is quite a long name),
both may be referenced using the :external:rst:role:`py:attr` role.

From the examples above, ``Foo.prop_a`` can be referenced using


``:dispatcherproperty:`Foo.prop_a```
    :dispatcherproperty:`Foo.prop_a <prop_foo.Foo.prop_a>`

``:attr:`Foo.prop_a```
    :attr:`Foo.prop_a <prop_foo.Foo.prop_a>`

``:obj:`Foo.prop_a```
    :obj:`Foo.prop_a <prop_foo.Foo.prop_a>`

And ``Baz.event_a`` can be referenced using

``:event:`Baz.event_a```
    :event:`Baz.event_a <event_baz.Baz.event_a>`

``:attr:`Baz.event_a```
    :attr:`Baz.event_a <event_baz.Baz.event_a>`

``:obj:`Baz.event_a```
    :obj:`Baz.event_a <event_baz.Baz.event_a>`
