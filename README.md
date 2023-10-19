# dh5 library

![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CodeFactor](https://www.codefactor.io/repository/github/kyrylo-gr/dh5/badge/main)](https://www.codefactor.io/repository/github/kyrylo-gr/dh5/overview/main)
[![Download Stats](https://img.shields.io/pypi/dm/dh5)](https://pypistats.org/packages/dh5)
[![Documentation](https://img.shields.io/badge/docs-blue)](https://kyrylo-gr.github.io/dh5/)

## Install

`pip install dh5`

## Installation in dev mode

`pip install -e .[dev]` or `python setup.py develop`

## Usage

```python
>>> sd = DH5('somedata.h5', 'w')
>>> sd['a'] = 5
>>> sd.save()

>>> sd_read = DH5('somedata.h5', 'r')
>>> sd_read['a']
5
>>> sd_read.a
5

>>> sd_append = DH5('somedata.h5', 'a')
>>> sd_append['b'] = 6
>>> sd_append.save()

>>> sd_read = DH5('somedata.h5', 'r')
>>> sd_read['a'], sd_read['b']
(5, 6)
```

To see more look at [the documentation](https://kyrylo-gr.github.io/dh5/)
