"""JSON module.

Problems with classical json that are solved:
- When loading, int and float values are strings. So `read` function uses `NumbersDecoder` by default.
- When dumping, object that can be converted to string or list are not converted.
 So `write` function converts objects to string and iterable to list.


Examples:
---------
Write to file:
```
from dh5 import jsn
data = {'a': 1}
jsn.write(path, data)
```

Open file:

```
from dh5 import jsn
data = jsn.read(path)
```
"""
from .methods import read, write  # noqa: F401
