---
title: Partially load.
---

## Use case

You have a huge file that there's no need to open.

Let's create file with some data:

```python
data = {"a": 1, "b": 2}
dh5.save(data, DATA_FILE_PATH, overwrite=True)
```

## Open file without loading all

Put `open_on_init=False`

```python
file = dh5.load(DATA_FILE_PATH, open_on_init=False)
```

In this case `file` consist of:

```
DH5 (r):
 {}
Unloaded keys: {'b', 'a'}
```

## Read a key

Use classical syntax to read a key and if it wasn't yet loaded it will be.

```python
file["a"]
```
