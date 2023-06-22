import pytest

@pytest.fixture(autouse=True)
def dispatcher_cleanup():
    import pydispatch
    pydispatch._GLOBAL_DISPATCHER._Dispatcher__events.clear()
    pydispatch.decorators._CACHED_CALLBACKS.cache.clear()
    yield
    pydispatch._GLOBAL_DISPATCHER._Dispatcher__events.clear()
    pydispatch.decorators._CACHED_CALLBACKS.cache.clear()
