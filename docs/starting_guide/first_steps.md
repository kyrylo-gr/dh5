# Getting Started with DH5

Make sure you have [installed the package](install.md) before.

# Writing Data

To save data to an HDF5 file:

```python
>>> sd = DH5('somedata.h5', 'w')
>>> sd['a'] = 5
>>> sd.save()
```

Alternatively, use the `save_on_edit` option:

```python
>>> sd = DH5('somedata.h5', 'w', save_on_edit=True)
>>> sd['a'] = 5
```

If file already exists, you should prefer to use `open_overwrite` method to be more explicit.

```python
>>> sd = DH5.overwrite('somedata.h5', save_on_edit=True)
>>> sd['a'] = 5
```

## Reading Data

Open an HDF5 file in read mode:

```python
>>> sd_read = DH5('somedata.h5', 'r')
>>> sd_read['a']  # Access data as an item
5
>>> sd_read.a  # Access data as an attribute
5
```

## Appending Data

To add data to an existing HDF5 file:

```python
>>> sd_append = DH5('somedata.h5', 'a')
>>> sd_append['b'] = 6
>>> sd_append.save()
```

## Locking Keys

You can lock specific keys to prevent their modification:

```python
>>> sd = DH5({"key1": "value1", "key2": "value2"})
>>> sd.lock_data(['key1', 'key2'])
>>> sd['key1'] = 2  # This will raise an error
ReadOnlyKeyError: "Cannot change a read-only key 'key1'."
```

To unlock a specific key:

```python
>>> sd.unlock_data('key2')
>>> sd['key2'] = 5
```

To lock all keys:

```python
>>> sd.lock_data()
```

# H5NpArray: Synchronous Array and File Modification

The `H5NpArray` class, integrated within the `H5PY` framework, allows for synchronous modification of `np.ndarray` and the corresponding file. When you change the array, the file is automatically updated, ensuring that your data is always in sync.

## Guideline for H5NpArray

### Open File in Write Mode:

```python
from labmate.syncdata import SyncData
sd = SyncData('tmp_data/test.h5', 'w', save_on_edit=True)
```

### Define New Item as a H5NpArray:

```python
shape = (100, 1000)
sd['test_array'] = sd.h5nparray(np.zeros(shape))
```

The `H5NpArray` class requires an `np.array` as a parameter to initialize the data inside the file.

### Modify Array as Normal

```python
for i in range(100):
    sd['test_array'][i, :] = np.random.random(1000)
# on each iteration only modified values are be saved.
```

### Verify Data Save

```python
read = SyncData('tmp_data/test.h5')
read['test_array'] # return the random array
```

# Further Details

To learn even more about how dh5 is structured, explore the [Advanced Examples](advanced_examples.md).
