"""All types used for typing inside dh5 module."""

from typing import Callable, Optional, Protocol, Union

import numpy as np


class ClassWithAsdict(Protocol):
    """Any class with predefined `_asdict` attribute.
    `_asdict` class should return a dictionary with only list and dict.
    It should not be a dict of other classes
    """

    def asdict(self) -> dict:  # type: ignore
        """Return internal data as a dictionary."""


class ClassWithAsarray(Protocol):
    """Any class with predefined `asarray` attribute.
    `asarray` class should return a np.ndarray.
    """

    def asarray(self) -> Union[np.ndarray, list]:  # type: ignore
        """Return internal data as an array."""


DICT_OR_LIST_LIKE = Optional[
    Union[
        dict,
        list,
        np.ndarray,
        ClassWithAsdict,
        ClassWithAsarray,
        np.int_,
        np.floating,
        float,
        int,
        str,
        Callable,
    ]
]
RIGHT_DATA_TYPE = Union[dict, np.ndarray, np.int_, np.floating, float, int]
