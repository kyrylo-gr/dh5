"""Module contains the errors used inside DH5."""


from typing import Optional, Set, Union


class FileLockedError(Exception):
    """Exception raised when a file is locked."""


class ReadOnlyKeyError(KeyError):
    """Exception raised when a key or set of keys is read-only."""

    def __init__(self, key: Optional[Union[str, Set[str]]] = None, action="change"):
        if isinstance(key, str):
            self.message = f"Cannot {action} a read-only key '{key}'."
        elif isinstance(key, (list, tuple, set)):
            self.message = f"Cannot {action} a read-only keys {key}."
        else:
            self.message = f"Cannot {action} a read-only object."
        super().__init__(self.message)
