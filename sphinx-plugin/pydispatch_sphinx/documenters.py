import typing as tp

from docutils.statemachine import StringList
import sphinx
from sphinx.application import Sphinx
from sphinx.locale import _, __
from sphinx.util import logging
from sphinx.util import inspect
from sphinx.util.typing import (
    get_type_hints, restify, stringify as stringify_typehint,
)
from sphinx.ext.autodoc import (
    ClassDocumenter, ModuleDocumenter, MethodDocumenter, AttributeDocumenter,
    PropertyDocumenter as _PropertyDocumenter, INSTANCEATTR,
    annotation_option, bool_option,
)

from pydispatch import Event
from pydispatch.properties import Property, DictProperty, ListProperty
_Event_fullname = '.'.join([Event.__module__, Event.__qualname__])

logger = logging.getLogger(__name__)

def has_event_name(member: tp.Any, membername: str, parent: ClassDocumenter) -> bool:
    objcls = parent.object

    # This will be False until #13 is merged
    # (https://github.com/nocarryr/python-dispatch/pull/13)
    # Once it's merged, everything below these two lines can be removed
    if hasattr(objcls, '_EVENTS_'):
        return membername in objcls._EVENTS_

    def iter_bases(_cls):
        if _cls is not object:
            yield _cls
            for b in _cls.__bases__:
                yield from iter_bases(b)

    for _cls in iter_bases(objcls):
        evts = getattr(_cls, '_events_', [])
        if membername in evts:
            return True
    return False

def update_event_content(object_name: str, more_content: StringList) -> None:
    objref = f':py:class:`pydispatch.Event <{_Event_fullname}>`'
    more_content.append(_(f'``{object_name}`` is a {objref} object.'), '')
    more_content.append('', '')


class DispatcherEventAttributeDocumenter(AttributeDocumenter):
    objtype = 'event'
    directivetype = 'event'
    member_order = 60
    priority = AttributeDocumenter.priority + 2
    option_spec = dict(AttributeDocumenter.option_spec)

    # def should_suppress_directive_header(self):
    #     return True

    @classmethod
    def can_document_member(
        cls, member: tp.Any, membername: str, isattr: bool, parent: tp.Any
    ) -> bool:
        if member is INSTANCEATTR and not isinstance(parent, ModuleDocumenter):
            anno = get_type_hints(parent.object)
            obj_anno = anno.get(membername)
            if obj_anno is Event:
                # logger.info(f'"{member!s}", {member.__class__=}, {membername=}')
                return True
        return False

    def update_content(self, more_content: StringList) -> None:
        super().update_content(more_content)
        update_event_content(self.objpath[-1], more_content)


class DispatcherEventMethodDocumenter(MethodDocumenter):
    objtype = 'eventmethod'
    directivetype = 'event'
    member_order = 60
    priority = MethodDocumenter.priority + 1
    option_spec = dict(MethodDocumenter.option_spec)
    option_spec['hasargs'] = bool_option

    @classmethod
    def can_document_member(
        cls, member: tp.Any, membername: str, isattr: bool, parent: tp.Any
    ) -> bool:
        if inspect.isroutine(member) and not isinstance(parent, ModuleDocumenter):
            return has_event_name(member, membername, parent)
        return False

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        sourcename = self.get_sourcename()
        self.add_line('   :hasargs:', sourcename)

    def add_content(self, more_content: tp.Optional[StringList]) -> None:
        if more_content is None:
            more_content = StringList()
        update_event_content(self.object_name, more_content)
        super().add_content(more_content)


class DispatcherPropertyDocumenter(AttributeDocumenter):
    objtype = 'dispatcherproperty'
    directive = 'dispatcherproperty'
    member_order = 60
    priority = _PropertyDocumenter.priority + 1
    option_spec = dict(AttributeDocumenter.option_spec)
    option_spec.update({
        'propcls':annotation_option,
    })

    @classmethod
    def can_document_member(
        cls, member: tp.Any, membername: str, isattr: bool, parent: tp.Any
    ) -> bool:

        if isinstance(parent, ClassDocumenter):
            if isinstance(member, Property):
                return True
        return False

    @property
    def propcls(self) -> str:
        r = getattr(self, '_propcls', None)
        if r is None:
            r = self._propcls = f'pydispatch.properties.{self.object.__class__.__name__}'
        return r

    def document_members(self, all_members: bool = False) -> None:
        pass

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        sourcename = self.get_sourcename()

        propcls = self.propcls
        assert propcls.endswith('Property')
        if propcls.endswith('DictProperty'):
            prop_type = 'dict'
        elif propcls.endswith('ListProperty'):
            prop_type = 'list'
        else:
            prop_type = None

        self.add_line(f'   :propcls: {propcls}', sourcename)
        prop_default = self.object.default

    def update_content(self, more_content: StringList) -> None:
        super().update_content(more_content)
        clsname = self.propcls.split('.')[-1]
        objref = f':py:class:`pydispatch.{clsname} <{self.propcls}>`'
        default = self.object.default
        s = f'``{self.object_name}`` is a {objref} object'
        if isinstance(self.object, (DictProperty, ListProperty)) and not len(default):
            s = f'{s}.'
        else:
            default = restify(self.object.default)
            s = f'{s} and defaults to ``{default}``.'
        more_content.append(_(s), '')
        more_content.append('', '')


def setup(app: Sphinx) -> None:
    app.setup_extension('sphinx.ext.autodoc')
    app.add_autodocumenter(DispatcherPropertyDocumenter)
    app.add_autodocumenter(DispatcherEventMethodDocumenter)
    app.add_autodocumenter(DispatcherEventAttributeDocumenter)
