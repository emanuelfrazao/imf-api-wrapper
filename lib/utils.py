from typing import Mapping, Iterable

def get_nested_value(data: Mapping, keys: Iterable) -> object:
    for i, key in enumerate(keys):
        try:
            data = data[key]
        except KeyError:
            raise KeyError(f"Key {key!r} not found in `data[{']['.join(keys[:i])}]`")
    return data

