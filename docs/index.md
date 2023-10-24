# Dictionary H5

The `Dictionary H5` provides an intuitive interface for manipulating HDF5 files, allowing them to be handled like traditional Python dictionaries.

- Concerned about losing your data in case of a kernel crash?
  `DH5` has a save_on_edit method to ensure your data is **always saved**.

- Need to update a single element in an array without a full re-save?
  No problem – `DH5` **only updates the changes** you make.

- Want to save tricky data like strings, mixed object arrays, or even functions, which can be challenging with `h5py`?
  `DH5` simplifies the process of **saving a wide variety of object types**.

## Features:

- **Dictionary-like Interface**: Access and modify HDF5 files using familiar dictionary syntax.
- **Save on Edit**: Automatically save changes to the file without manually calling a save method (when `save_on_edit=True` is provided).
- **Multiple Opening Modes**: Open files in different modes like 'read', 'write', and 'append'.
- **Key Locking**: Lock specific keys to prevent their modification.

Give `dh5` a try and streamline your data management.

# Install

`pip install dh5`

More on it can be found inside the [installation guide](starting_guide/install.md)

# Usage

```python
# Save {'a': 5} to `somedata.h5`
>>> sd = DH5('somedata.h5', 'w')
>>> sd['a'] = 5
>>> sd.save()

# Open 'somedata.h5' in read mode
>>> sd_read = DH5('somedata.h5', 'r')
>>> sd_read['a'] # access data as an item
5
>>> sd_read.a # access data as an attribute
5

# Open 'somedata.h5' in append mode. Allows to add data to existing file.
>>> sd_append = DH5('somedata.h5', 'a')
>>> sd_append['b'] = 6
>>> sd_append.save()

# In the end, `samedata.h5` contains {'a': 5, 'b': 6}
>>> sd_read = DH5('somedata.h5', 'r')
>>> sd_read['a'], sd_read['b']
(5, 6)
```

For further insight, please refer to the [First Steps guide](starting_guide/first_steps.md).

For more in-depth information, explore the [Advanced Examples](starting_guide/advanced_examples.md).

To gain a comprehensive understanding of syntax, visit the [DH5 Class Page](dh5).
