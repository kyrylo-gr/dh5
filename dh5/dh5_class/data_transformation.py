"""Data transformation utils."""

import json
import logging
from typing import Iterable, List, Literal, Optional, Sized, Tuple

import numpy as np

from ..types import DICT_OR_LIST_LIKE

_JSON_WARN_AUTO_THRESHOLD = 1000  # estimated JSON bytes before auto-warning fires


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


def transform_not_dict_on_save(value, level=0):
    """Transform data during saving of h5 file if data is not a dict."""
    if isinstance(value, np.ndarray):
        if level == 0:
            return value
        return value.tolist()

    if isinstance(value, (list)) and (np_array_check(value) < 0):
        try:
            if level == 0:
                return "__json__" + json.dumps(value)
            return value
        except TypeError:
            value_transformed = [
                transform_not_dict_on_save(v, level=level + 1) for v in value
            ]
            return "__json__" + json.dumps(value_transformed)

    if callable(value):
        from .transformation_types import function_save

        return "__function__" + function_save.function_to_str(value)

    return value


def get_storage_type(value) -> str:
    """Return how *value* will be stored in the HDF5 file.

    Returns one of: ``"array"``, ``"json"``, ``"function"``, ``"group"``, ``"scalar"``.
    """
    if isinstance(value, np.ndarray):
        return "array"
    if isinstance(value, list):
        return "json" if np_array_check(value) < 0 else "array"
    if callable(value):
        return "function"
    if isinstance(value, dict):
        return "group"
    return "scalar"


def _estimate_json_size(value) -> int:
    """Rough estimate of how many bytes the JSON-encoded form of *value* would take."""
    try:
        return len(json.dumps(value))
    except (TypeError, ValueError):
        return 0


def find_json_conversions(
    data: dict, prefix: str = ""
) -> List[Tuple[str, int]]:
    """Walk *data* recursively and return (key_path, estimated_bytes) for every
    value that will be JSON-encoded when saved to HDF5.
    """
    results: List[Tuple[str, int]] = []
    for key, value in data.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict):
            results.extend(find_json_conversions(value, prefix=path + "/"))
        elif isinstance(value, list) and np_array_check(value) < 0:
            results.append((path, _estimate_json_size(value)))
        elif callable(value):
            results.append((path, 0))
    return results


def warn_json_conversions(
    data: dict,
    mode: Literal["all", "auto", "mute"] = "auto",
) -> None:
    """Issue warnings for values in *data* that will be JSON-encoded on save.

    Args:
        data: The dictionary of values to inspect.
        mode: Warning verbosity.
            ``"all"``  – warn for every JSON-converted value.
            ``"auto"`` – warn only when the estimated payload exceeds
                         ``_JSON_WARN_AUTO_THRESHOLD`` bytes.
            ``"mute"`` – never warn.
    """
    if mode == "mute":
        return
    for key_path, size in find_json_conversions(data):
        if mode == "all" or (mode == "auto" and size >= _JSON_WARN_AUTO_THRESHOLD):
            logging.warning(
                "DH5: key '%s' will be stored as a JSON string in the HDF5 file "
                "(estimated size: %d bytes). Consider using a numpy array for "
                "better performance.",
                key_path,
                size,
            )
