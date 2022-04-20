import typing as tp

from docutils.statemachine import StringList
import sphinx
from sphinx.application import Sphinx
from sphinx.locale import _, __
from sphinx.util import logging
from sphinx.util.typing import (
    get_type_hints, restify, stringify as stringify_typehint,
)
from sphinx.ext.autodoc import (
    ClassDocumenter, AttributeDocumenter, annotation_option,
    PropertyDocumenter as _PropertyDocumenter,
)

from pydispatch.properties import Property, DictProperty, ListProperty

logger = logging.getLogger(__name__)


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

    def string_list_repr(self): # pragma: no cover
        sl = self.directive.result
        l = []
        for line in sl.xitems():
            l.append('{}:{}:{}'.format(*line))
        return '\n'.join(l)

    def log_string_list(self, log_str: tp.Optional[str] = None): # pragma: no cover
        return
        if log_str is None:
            log_str = ''
        s = self.string_list_repr()
        logger.info(f'{log_str}{s}')

    def document_members(self, all_members: bool = False) -> None:
        pass

    def add_directive_header(self, sig: str) -> None:
        super().add_directive_header(sig)
        self.log_string_list('Attrib directive_header: \n')
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
        # self.add_line(f'   :value: {prop_default}', sourcename)
        # if True:
        #     pass
        # elif self.options.annotation:
        #     self.add_line(f'   :annotation: {self.options.annotation}', sourcename)
        # else:
        #     if self.config.autodoc_typehints != 'none':
        #         annotations = get_type_hints(
        #             self.parent, None, self.config.autodoc_type_aliases,
        #         )
        #         if self.objpath[-1] in annotations:
        #             objrepr = stringify_typehint(annotations.get(self.objpath[-1]))
        #             self.add_line(f'   :type: {objrepr}', sourcename)
        #         elif prop_type is not None:
        #             self.add_line(f'   :type: {prop_type}', sourcename)

        # if prop_type is not None:
        #     self.add_line(f'    :type: {prop_type}', sourcename)
        self.log_string_list('Prop directive_header: \n')


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
        self.log_string_list('update_content:\n')


def setup(app: Sphinx) -> None:
    app.setup_extension('sphinx.ext.autodoc')
    app.add_autodocumenter(DispatcherPropertyDocumenter)
