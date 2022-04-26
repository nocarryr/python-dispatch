Reference
=========

Directives
----------

.. rst:directive:: .. py:event:: event_name

    Describes a :class:`pydispatch.dispatch.Event` object.  This directive
    inherits from Sphinx's :rst:dir:`py:method` directive to allow
    representation of arguments.

    .. rst:directive:option:: hasargs: Indicates if there are event arguments to document
        :type: bool


.. rst:directive:: .. py:dispatcherproperty:: property_name

    Describes a :class:`pydispatch.properties.Property` object. This directive
    inherits from Sphinx's :rst:dir:`py:attribute` directive.

    .. rst:directive:option:: propcls: The Property class defined
        :type: str

    .. rst:directive:option:: type: Expected type of the Property
        :type: type

Roles
-----

.. rst:role:: py:event

    References a :class:`pydispatch.dispatch.Event` object

.. rst:role:: py:dispatcherproperty

    References a :class:`pydispatch.properties.Property` object


Autodoc Directives
------------------

The following directives are added as part of the :mod:`sphinx.ext.autodoc`
integration.

In most cases, they would not be used directly. The :rst:dir:`automodule` and
:rst:dir:`autoclass` directives will use them as it would for any other
class-level documenter.

.. rst:directive:: autoevent

    Document :class:`~pydispatch.dispatch.Event` objects as instance attributes
    using the :rst:dir:`py:event` directive. Inherited from :rst:dir:`autoattribute`.

.. rst:directive:: autoeventmethod

    Document :class:`~pydispatch.dispatch.Event` objects as methods using the
    :rst:dir:`py:event` directive. Inherited from :rst:dir:`automethod`.

    .. rst:directive:option:: hasargs: Indicates if there are arguments to document
        :type: bool

.. rst:directive:: autodispatcherproperty

    Document :class:`~pydispatch.properties.Property` objects using the
    :rst:dir:`py:dispatcherproperty` directive. Inherited from :rst:dir:`autoattribute`.

    .. rst:directive:option:: propcls: The Property class defined
        :type: str

    .. rst:directive:option:: type: Expected type of the Property
        :type: type
