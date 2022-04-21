import typing as tp

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx import addnodes
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.locale import _, __
from sphinx.domains import ObjType
from sphinx.domains.python import (
    PyXRefRole, PyAttribute, PyMethod, PyObject, type_to_xref,
)

from pydispatch.dispatch import Event
_Event_fullname = '.'.join([Event.__module__, Event.__qualname__])

logger = logging.getLogger(__name__)

class DispatcherPropertyDirective(PyAttribute):
    option_spec = PyAttribute.option_spec.copy()
    option_spec.update({
        'propcls':directives.unchanged,
    })

    def get_signature_prefix(self, sig: str) -> tp.List[nodes.Node]:
        propcls = self.options.get('propcls')
        return [
            addnodes.desc_type(propcls, '',
                type_to_xref(propcls, self.env, suppress_prefix=True),
                addnodes.desc_sig_space(),
            ),
        ]

class DispatcherEventMethodDirective(PyMethod):
    option_spec = PyMethod.option_spec.copy()
    option_spec['hasargs'] = directives.flag
    option_spec['type'] = directives.unchanged

    def needs_arglist(self) -> bool:
        return 'hasargs' in self.options

    def get_signature_prefix(self, sig: str) -> tp.List[nodes.Node]:
        return [
            type_to_xref(_Event_fullname, self.env, suppress_prefix=True),
            addnodes.desc_sig_space(),
        ]


def setup(app: Sphinx) -> None:
    app.setup_extension('sphinx.directives')
    directive_name = 'dispatcherproperty'

    app.add_directive_to_domain('py', directive_name, DispatcherPropertyDirective)
    propertyobj_role = PyXRefRole()
    app.add_role_to_domain('py', directive_name, propertyobj_role)

    app.add_directive_to_domain('py', 'event', DispatcherEventMethodDirective)
    event_role = PyXRefRole()
    app.add_role_to_domain('py', 'event', event_role)

    property_obj_type = ObjType(_('Property'), directive_name, 'attr', 'obj')
    event_obj_type = ObjType(_('Event'), 'event', 'attr', 'obj')
    object_types = app.registry.domain_object_types.setdefault('py', {})
    object_types[directive_name] = property_obj_type
    object_types['event'] = event_obj_type
