<h1 align="center">
<img src="docs/images/dh5-logo.png" width="400">
</h1><br>

<div align="center">

[![Pypi](https://img.shields.io/pypi/v/dh5.svg)](https://pypi.org/project/dh5/)
![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CodeFactor](https://www.codefactor.io/repository/github/kyrylo-gr/dh5/badge/main)](https://www.codefactor.io/repository/github/kyrylo-gr/dh5/overview/main)
[![Coverage Status](https://coveralls.io/repos/github/kyrylo-gr/dh5/badge.svg?branch=main)](https://coveralls.io/github/kyrylo-gr/dh5?branch=main)
[![Download Stats](https://img.shields.io/pypi/dm/dh5)](https://pypistats.org/packages/dh5)
[![Documentation](https://img.shields.io/badge/docs-blue)](https://kyrylo-gr.github.io/dh5/)

</div>

`Dictionary H5` — a package that enables the seamless manipulation of HDF5 files by treating them like traditional dictionaries.

- Concerned about losing your data in case of a kernel crash?
  `DH5` has a save_on_edit method to ensure your data is **always saved**.

- Need to update a single element in an array without a full re-save?
  No problem – `DH5` **only updates the changes** you make.

- Want to save tricky data like strings, mixed object arrays, or even functions, which can be challenging with `h5py`?
  `DH5` simplifies the process of **saving a wide variety of object types**.

Give `dh5` a try and streamline your data management.

## Install

`pip install dh5`

## Installation in dev mode

`pip install -e .[dev]` or `python setup.py develop`

## Usage

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

To see more look at [the documentation](https://kyrylo-gr.github.io/dh5/)
