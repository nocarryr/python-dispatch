from typing import Optional
from pydispatch import Dispatcher

class Spam(Dispatcher):
    """Summary line
    """

    _events_ = ['value_changed']

    def value_changed(self, new_value: int, old_value: Optional[int], **kwargs):
        """Description of value_changed
        """
        pass
