# H5NpArray

In `H5PY` `np.ndarray` can be saved as soon as modified. To do that there exists a class `H5NpArray`. This class synchronously modifies the np.ndarray and file.

## Guideline

1. Open file in write mode.

```python
from labmate.DH5 import DH5
sd = DH5('tmp_data/test.h5', overwrite=True, save_on_edit=False)
```

2. Define new item as a h5nparray

```python
shape = (100, 1000)
sd['test_array'] = sd.h5nparray(np.zeros(shape))
```

`H5NpArray` takes the np.array as parameter to initialize the data inside the file.

3. Modify as normal

```python
for i in range(100):
    sd['test_array'][i, :] = np.random.random(1000)
```

4. Check that data was saved

```python
read = DH5('tmp_data/test.h5')
read['test_array']
```

## Implementation

- `H5NpArray` has `__should_not_be_converted__=True`, which prevents `DH5` from converting it to an array and continuous using as a class

- as soon as you run `fd[key]` it will run method `__init__filepath__` to provide the filepath and the key to the class `H5NpArray`
