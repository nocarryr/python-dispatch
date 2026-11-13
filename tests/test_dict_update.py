import pytest

from pydispatch import DictProperty, Dispatcher
from pydispatch.properties import ObservableDict, ObservableList


class KeysOnlyMapping:
    def __init__(self, values):
        self.values = values

    def keys(self):
        return self.values.keys()

    def __getitem__(self, key):
        return self.values[key]


class FailingMapping:
    def keys(self):
        return ['added', 'bad']

    def __getitem__(self, key):
        if key == 'bad':
            raise RuntimeError('mapping failed')
        return 2


@pytest.mark.parametrize('copy_on_change', [False, True])
@pytest.mark.parametrize('kind', ['mapping', 'keys', 'pairs', 'generator', 'kwargs'])
def test_update_accepts_dict_inputs_and_notifies_once(listener, copy_on_change, kind):
    class Sender(Dispatcher):
        data = DictProperty({'unchanged': 1, 'replace': 0}, copy_on_change=copy_on_change)

    sender = Sender()
    sender.bind(data=listener.on_prop)
    pairs = [('unchanged', 1), ('replace', 2), ('nested', [3])]
    if kind == 'mapping':
        result = sender.data.update(dict(pairs), replace=4)
    elif kind == 'keys':
        result = sender.data.update(KeysOnlyMapping(dict(pairs)), replace=4)
    elif kind == 'pairs':
        result = sender.data.update(pairs, replace=4)
    elif kind == 'generator':
        result = sender.data.update(iter(pairs), replace=4)
    else:
        result = sender.data.update(unchanged=1, replace=4, nested=[3])

    assert result is None
    assert sender.data == {'unchanged': 1, 'replace': 4, 'nested': [3]}
    assert isinstance(sender.data['nested'], ObservableList)
    assert sender.data['nested'].parent_observable is sender.data
    assert len(listener.property_events) == 1
    assert set(listener.property_event_kwargs[0]['keys']) == {'replace', 'nested'}
    assert listener.property_event_kwargs[0]['old'] == (
        {'unchanged': 1, 'replace': 0} if copy_on_change else None
    )


@pytest.mark.parametrize('copy_on_change', [False, True])
def test_update_notifies_partial_changes_and_restores_state_on_error(listener, copy_on_change):
    class Sender(Dispatcher):
        data = DictProperty({'before': [1]}, copy_on_change=copy_on_change)

    sender = Sender()
    sender.bind(data=listener.on_prop)
    with pytest.raises(ValueError):
        sender.data.update([('added', [2]), ('invalid',)])
    assert sender.data == {'before': [1], 'added': [2]}
    assert isinstance(sender.data['added'], ObservableList)
    assert len(listener.property_events) == 1
    assert listener.property_event_kwargs[0]['keys'] == ['added']
    assert listener.property_event_kwargs[0]['old'] == (
        {'before': [1]} if copy_on_change else None
    )
    sender.data['after'] = 3
    assert len(listener.property_events) == 2


def test_update_duplicate_keys_and_invalid_first_pair(listener):
    class Sender(Dispatcher):
        data = DictProperty({'key': 1}, copy_on_change=True)

    sender = Sender()
    sender.bind(data=listener.on_prop)
    sender.data.update([('key', 2), ('key', 1)])
    assert sender.data == {'key': 1}
    assert listener.property_event_kwargs[0]['keys'] == ['key']
    with pytest.raises(ValueError):
        sender.data.update([('invalid',)])
    assert len(listener.property_events) == 1
    sender.data.update()
    assert len(listener.property_events) == 2
    assert listener.property_event_kwargs[-1]['keys'] == []


def test_update_failing_mapping_and_dictionary_keywords(listener):
    class Sender(Dispatcher):
        data = DictProperty(copy_on_change=True)

    sender = Sender()
    sender.bind(data=listener.on_prop)
    with pytest.raises(RuntimeError, match='mapping failed'):
        sender.data.update(FailingMapping())
    assert sender.data == {'added': 2}
    assert listener.property_event_kwargs[0]['old'] == {}
    assert listener.property_event_kwargs[0]['keys'] == ['added']
    sender.data.update(other=3)
    assert sender.data['other'] == 3
    with pytest.raises(TypeError):
        sender.data.update({}, {})
    assert len(listener.property_events) == 2


def test_copy_on_change_deep_copies_nested_containers(listener):
    class Sender(Dispatcher):
        data = DictProperty({'items': [{'nested': [1]}]}, copy_on_change=True)

    sender = Sender()
    sender.bind(data=listener.on_prop)
    sender.data['items'][0]['nested'].append(2)
    old = listener.property_event_kwargs[0]['old']
    assert old == {'items': [{'nested': [1]}]}
    assert type(old) is dict
    assert type(old['items']) is list
    assert type(old['items'][0]) is dict
    assert type(old['items'][0]['nested']) is list
    assert isinstance(sender.data, ObservableDict)
