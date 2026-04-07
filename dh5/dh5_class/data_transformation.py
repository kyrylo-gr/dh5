"""Data transformation utils."""

import json
import logging
from typing import Iterable, Optional, Sized

import numpy as np

from ..types import DICT_OR_LIST_LIKE


def np_array_check(lst, size: Optional[int] = None) -> int:
    """Check if the list can be converted to np.ndarray.

    Args:
        lst (list|np.ndarray): Any list
        size (int, optional): Expected size. Defaults to None.

    Returns:
        int: size of the list if it can be converted to np.ndarray, -1 otherwise.

    Examples:
    --------
    [[1, 2], [2, 3], [3, 4]] -> Can be converted to np.ndarray. Return 3.
    [1, [2, 3], 4] -> Cannot be converted to np.ndarray. Return -1.

    """
    if (
        isinstance(lst, Iterable)
        and isinstance(lst, Sized)
        and not isinstance(lst, str)
    ):
        # if isinstance(lst, (list, np.ndarray)):
        if size is not None and size != len(lst):
            return -1  # pragma: no cover
        for lst_elm in lst:
            check = np_array_check(lst_elm, size)
            if check >= 0:
                size = check
            else:
                return -1
        return len(lst)
    if isinstance(lst, (np.number)):
        return 0
    return -1


def transform_to_possible_formats(data: DICT_OR_LIST_LIKE) -> DICT_OR_LIST_LIKE:
    """Transform data to possible formats on setitem.

    If data can be converted to dict or np.ndarray, it will be converted.
    Unless it has attribute __should_not_be_converted__ set to True. Then nothing happens and data
    will be converted during saving.
    """
    if hasattr(data, "__should_not_be_converted__") and data.__should_not_be_converted__ is True:  # type: ignore
        return data

    if hasattr(data, "asdict"):
        data = data.asdict()  # type: ignore

    if hasattr(data, "_asdict"):
        data = data._asdict()  # type: ignore

    if hasattr(data, "asarray"):
        data = data.asarray()  # type: ignore

    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = transform_to_possible_formats(value)
        return data

    if isinstance(data, (tuple, set)):
        data = list(data)

    if isinstance(data, list) and (np_array_check(data) < 0):
        return data

    return data


def transform_on_open(value):
    """Transform data during opening of h5 file."""
    if isinstance(value, bytes):
        value = value.decode()
    if isinstance(value, str) and value.startswith("__json__"):
        return json.loads(value[8:])
    if isinstance(value, str) and value.startswith("__function__"):
        from .transformation_types import function_save

        return function_save.Function(value[12:])
    return value


def _warn_json_conversion_if_needed(
    value_to_dump, converted_payload: str, mode: str, *, key: Optional[str] = None
):
    if mode == "mute":
        return
    if mode not in {"all", "auto"}:
        raise ValueError("json_conversion_mode should be one of: 'all', 'auto', 'mute'")
    if mode == "auto" and len(converted_payload) < 1024:
        return
    key_info = f" for key '{key}'" if key else ""
    logging.warning(
        "DH5 converted value%s to JSON string before saving (type=%s, approx_size=%dB).",
        key_info,
        type(value_to_dump).__name__,
        len(converted_payload),
    )


def transform_not_dict_on_save(
    value, level=0, *, json_conversion_mode: str = "auto", key: Optional[str] = None
):
    """Transform data during saving of h5 file if data is not a dict."""
    if isinstance(value, np.ndarray):
        if level == 0:
            return value
        return value.tolist()

    if isinstance(value, (list)) and (np_array_check(value) < 0):
        try:
            if level == 0:
                converted = json.dumps(value)
                _warn_json_conversion_if_needed(
                    value, converted, json_conversion_mode, key=key
                )
                return "__json__" + converted
            return value
        except TypeError:
            value_transformed = [
                transform_not_dict_on_save(
                    v, level=level + 1, json_conversion_mode="mute", key=key
                )
                for v in value
            ]
            converted = json.dumps(value_transformed)
            _warn_json_conversion_if_needed(
                value, converted, json_conversion_mode, key=key
            )
            return "__json__" + converted

    if callable(value):
        from .transformation_types import function_save

        return "__function__" + function_save.function_to_str(value)

    return value
