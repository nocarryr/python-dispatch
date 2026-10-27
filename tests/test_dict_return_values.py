import pytest

from pydispatch import Dispatcher, DictProperty


@pytest.mark.parametrize('copy_on_change', [False, True])
def test_pop_returns_removed_value_and_default(listener, copy_on_change):
    """Preserve dict return identity, exceptions and change notifications."""
    class Sender(Dispatcher):
        data = DictProperty(copy_on_change=copy_on_change)

    sender = Sender()
    sender.data['items'] = [1, 2]
    stored = sender.data['items']
    sender.bind(data=listener.on_prop)

    assert sender.data.pop('items') is stored
    assert sender.data == {}
    assert len(listener.property_events) == 1
    old = listener.property_event_kwargs[0]['old']
    assert old == ({'items':[1, 2]} if copy_on_change else None)

    fallback = object()
    assert sender.data.pop('missing', fallback) is fallback
    assert len(listener.property_events) == 2

    with pytest.raises(KeyError):
        sender.data.pop('missing')
    assert len(listener.property_events) == 2

    with pytest.raises(TypeError):
        sender.data.pop()
    assert len(listener.property_events) == 2


@pytest.mark.parametrize('copy_on_change', [False, True])
def test_setdefault_returns_inserted_or_existing_value(listener, copy_on_change):
    """Preserve inserted/existing return values and existing event behavior."""
    class Sender(Dispatcher):
        data = DictProperty(copy_on_change=copy_on_change)

    sender = Sender()
    sender.bind(data=listener.on_prop)
    default = object()

    assert sender.data.setdefault('key', default) is default
    assert sender.data['key'] is default
    assert len(listener.property_events) == 1
    old = listener.property_event_kwargs[0]['old']
    assert old == ({} if copy_on_change else None)

    assert sender.data.setdefault('key', object()) is default
    assert sender.data['key'] is default
    assert len(listener.property_events) == 2

    assert sender.data.setdefault('implicit') is None
    assert sender.data['implicit'] is None
    assert len(listener.property_events) == 3

    with pytest.raises(TypeError):
        sender.data.setdefault()
    assert len(listener.property_events) == 3
