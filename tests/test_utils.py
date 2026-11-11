import gc

import pytest

from pydispatch.utils import InformativeWVDict


class WeakValue:
    pass


def test_informative_weak_dict_notifies_on_explicit_deletion():
    deleted = []
    values = InformativeWVDict(del_callback=deleted.append)
    value = WeakValue()
    values['key'] = value

    del values['key']

    assert deleted == ['key']
    assert 'key' not in values


def test_informative_weak_dict_notifies_when_value_is_collected():
    deleted = []
    values = InformativeWVDict(del_callback=deleted.append)
    value = WeakValue()
    values['key'] = value

    del value
    gc.collect()

    assert deleted == ['key']
    assert 'key' not in values


def test_informative_weak_dict_without_callback_still_raises_on_deletion():
    values = InformativeWVDict()
    value = WeakValue()
    values['key'] = value

    with pytest.raises(TypeError):
        del values['key']

    assert 'key' not in values
