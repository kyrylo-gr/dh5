"""DH5 module. Main class is DH5. It's a dictionary that is synchronized with .h5 file.

Also this module contains h5py_utils that allows to save and load dict from a h5 file.

Examples:
---------
>>> from dh5 import DH5
>>> data = DH5("some_file.h5", mode='w')
>>> data["some_key"] = "some_value"
>>> data.save()

>>> data = DH5("some_file.h5", mode='r')
>>> data["some_key"] # -> "some_value"
>>> data["some_key"] = "some_other_value" # -> KeyError: Cannot change value in read mode

"""


# flake8: noqa: F401
from .main import DH5
