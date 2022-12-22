from typing import Iterable
    
def is_non_string_iterable(x: object) -> bool:
    return isinstance(x, Iterable) and not isinstance(x, str)