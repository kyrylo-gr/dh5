"""DH5 class is a dictionary that is synchronized with .h5 file."""

import logging
import os
from collections.abc import Iterable
from copy import deepcopy
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Set, TypeVar, Union, overload

from ..errors import ReadOnlyKeyError
from ..types import DICT_OR_LIST_LIKE
from . import h5py_utils
from .data_transformation import transform_to_possible_formats
from .dict_structure import get_keys_structure, output_dict_structure
from .internal_classes import NotLoaded

# from ..utils import


def editing(func):
    """If a function changes the data it should be saved.
    It's a wrapper for such function.
    """

    @wraps(func)
    def run_func_and_clean_precalculated_results(self, *args, **kwargs):
        self._last_data_saved = False  # pylint: disable=W0212
        res = func(self, *args, **kwargs)
        self._clean_precalculated_results()  # pylint: disable=W0212
        if self._save_on_edit:  # pylint: disable=W0212
            self.save(only_update=True)
        return res

    return run_func_and_clean_precalculated_results


_T = TypeVar("_T")
_SELF = TypeVar("_SELF", bound="DH5")


class DH5:
    """DH5 - Dict that is synchronized with .h5 file.

    # Usage and initialization
    DH5 can open files in 3 different modes:

    - 'r' - Read mode. No data chan be modified.
    - 'w' - Write mode. If file exists it will be overwritten. And you have full control on data.
    - 'a' - Append mode. If file exists it will be opened. And you have full control on data.

    To overwrite file use `open_overwrite` method or `mode="w"` with `overwrite=True`.


    # Examples
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

    """

    _repr: Optional[str] = None
    _default_attr = ["get", "items", "keys", "pop", "update", "values", "save"]
    _last_data_saved: bool = False
    _filepath: Optional[str] = None
    _read_only: Union[bool, Set[str]]
    _raise_file_locked_error: bool = False
    _retry_on_file_locked_error: int = 5
    _last_time_data_checked: float = 0
    _file_modified_time: float = 0
    __should_initialized: bool = False
    __should_not_be_converted__ = True

    def __init__(
        self,
        filepath_or_data: Optional[Union[str, dict, Path]] = None,
        /,
        mode: Optional[Literal["r", "w", "a", "w=", "a="]] = None,
        *,
        filepath: Optional[Union[str, Path]] = None,
        save_on_edit: bool = False,
        read_only: Optional[Union[bool, Set[str]]] = None,
        overwrite: Optional[bool] = None,
        data: Optional[dict] = None,
        open_on_init: Optional[bool] = None,
        **kwds,
    ):
        """DH5.

        Args:
            filepath_or_data (str|dict, optional): either filepath, either data as dict.
            filepath (str|Path, optional): filepath to load. Defaults to None.
            save_on_edit (bool, optional): Save data as soon as you changed it.
                Defaults to False. And data should be saved using `save()` method.
            read_only (bool, optional): opens file in read_only mode, i.e. it cannot be modified.
                Defaults to (save_on_edit is False && overwrite is False) and filepath is set.
            overwrite (Optional[bool], optional):
                If file exists, it should be explicitly precised.
                By default raises an error if file exist.
            data (Optional[dict], optional):
                Data to load. If data provided, file . Defaults to None.
            open_on_init (Optional[bool], optional): open_on_init. Defaults to True.

        """
        if mode is not None:
            if mode.startswith("w"):
                read_only = False
            elif mode.startswith("a"):
                read_only = False
                overwrite = False
            elif mode == "r":
                read_only = True
            if mode.endswith("="):
                save_on_edit = True

        if filepath_or_data is not None and hasattr(filepath_or_data, "keys"):
            if not isinstance(filepath_or_data, dict):
                filepath_or_data = {key: filepath_or_data[key] for key in filepath_or_data.keys()}  # type: ignore
            data = data or filepath_or_data

        if isinstance(filepath_or_data, (str, Path)):
            filepath = filepath or filepath_or_data

        if filepath and not isinstance(filepath, str):
            filepath = str(filepath)

        self._data: Dict[str, Any] = data or {}
        # transform_to_possible_formats(self._data)
        self._keys: Set[str] = set(self._data.keys())
        self._last_update = set()
        self._save_on_edit = save_on_edit
        self._classes_should_be_saved_internally = set()
        self._key_prefix: Optional[str] = kwds.get("key_prefix")

        if read_only is None:
            read_only = (
                save_on_edit is False and not overwrite
            ) and filepath is not None

        if open_on_init is False and overwrite is True:
            raise ValueError("Cannot overwrite file and open_on_init=False mode")
        self._open_on_init = (
            open_on_init if open_on_init is not None else (None if self._data else True)
        )
        self._unopened_keys = set()

        # if keep_up_to_data and read_only is True:
        # raise ValueError("Cannot open file in read-only and keep_up_to_data=True mode")
        # self._keep_up_to_data = keep_up_to_data

        self._read_only = read_only
        if filepath is not None:
            filepath = filepath if filepath.endswith(".h5") else filepath + ".h5"

            if (overwrite or save_on_edit) and read_only:
                raise ValueError(
                    """Cannot open file in read_only mode and overwrite it."""
                )

            if os.path.exists(filepath):
                if overwrite is None and not read_only:
                    raise FileExistsError(
                        "File with the same name already exists. So you should explicitly "
                        "provide what to do with it. Set `overwrite=True` to replace file. "
                        "Set `overwrite=False` if you want to open existing file and work with it."
                    )

                if overwrite and not read_only:
                    self.__should_initialized = True
                    # os.remove(filepath)

                if read_only or (not read_only and not overwrite):
                    if self._open_on_init:
                        self._load_from_h5(filepath)
                    elif self._open_on_init is False:
                        self._keys = h5py_utils.keys_h5(
                            filepath, key_prefix=self._key_prefix
                        )
                        self._unopened_keys.update(self._keys)

            elif read_only:
                raise ValueError(
                    f"Cannot open file in read_only mode if file {filepath} does not exist"
                )

            # if not read_only:
            self._filepath = filepath

    @classmethod
    def open_overwrite(
        cls,
        filepath_or_data: Optional[Union[str, dict, Path]] = None,
        /,
        mode: Optional[Literal["="]] = None,
        *,
        filepath: Optional[Union[str, Path]] = None,
        save_on_edit: bool = False,
        read_only: Optional[Union[bool, Set[str]]] = None,
        overwrite: Optional[bool] = True,
        data: Optional[dict] = None,
        open_on_init: Optional[bool] = None,
        **kwds,
    ):
        """Open file in the overwrite mode.

        It deletes the file if it exists and then opens it in the write mode.
        Same syntax as `__init__` method.
        """
        mode_ = "w=" if mode == "=" else "w"
        return cls(
            filepath_or_data,
            mode=mode_,
            filepath=filepath,
            save_on_edit=save_on_edit,
            read_only=read_only,
            overwrite=overwrite,
            data=data,
            open_on_init=open_on_init,
            **kwds,
        )

    def __init__filepath__(
        self, *, filepath: str, filekey: str, save_on_edit: bool = False, **_
    ):
        """Initialize a filepath. It allows to save sub DH5 objects independently.

        Args:
            filepath (str): The path to the file to be synced.
            filekey (str): The key prefix to use for the synced data.
            save_on_edit (bool, optional): Whether to save the file automatically when it is edited. Defaults to False.
            **kwargs: Additional keyword arguments to pass to the constructor.
        """
        self._filepath = filepath
        self._key_prefix = filekey
        self._save_on_edit = save_on_edit

    def _load_from_h5(
        self, filepath: Optional[str] = None, key: Optional[Union[str, Set[str]]] = None
    ) -> Set[str]:
        """Load data from h5 to self._data."""
        filepath = filepath or self._filepath
        if filepath is None:
            raise ValueError("Filepath is not specified. So cannot load_h5")
        filepath = filepath if filepath.endswith(".h5") else filepath + ".h5"
        data = h5py_utils.open_h5(filepath, key=key, key_prefix=self._key_prefix)
        self._file_modified_time = os.path.getmtime(filepath)
        return self._update(data)

    def load(
        self, filepath: Optional[str] = None, key: Optional[Union[str, Set[str]]] = None
    ):
        """Load data from h5 into current object."""
        updated_from_other_file = filepath is not None
        updated_key = self._load_from_h5(filepath=filepath, key=key)
        if updated_from_other_file:
            for key in updated_key:
                self._keys.add(key)

        return self

    def lock_data(self: _SELF, keys: Optional[Iterable[str]] = None) -> _SELF:
        """Locks the specified keys in the database so they cannot be changed.

        Args:
            keys: An optional iterable of strings representing the keys to be locked.
            If None, all keys will be locked.

        Returns:
            A reference to the DH5 object.

        Raises:
            ValueError: If everything is already locked by read_only mode.

        Examples:
            >>> sd = DH5({"key1": "value1", "key2": "value2"})
            >>> sd.lock_data(['key1', 'key2'])
            >>> sd['key1'] = 2
            ReadOnlyKeyError: "Cannot change a read-only key 'key1'."
            >>> sd['key2'] = 5

        """
        if self._read_only is True:
            raise ValueError(
                "Cannot lock specific data and everything is locked by read_only mode"
            )
        if not isinstance(self._read_only, set):
            self._read_only = set()
        if keys is None:
            keys = self.keys()
        elif isinstance(keys, str):
            keys = (keys,)

        for key in keys:
            self._read_only.add(key)

        self._clean_precalculated_results()
        return self

    def unlock_data(self: _SELF, remove_keys: Optional[Iterable[str]] = None) -> _SELF:
        """Unlock the specified keys in the database so they can be changed.

        If file was opened in read-only mode you cannot unlock it, however you can open
        it again in 'a' mode and lock all keys except necessary.

        Args:
            keys: An optional iterable of strings representing the keys to be unlocked.
            If None, all keys will be unlocked.

        Returns:
            A reference to the DH5 object.

        Raises:
            ValueError: If everything is already locked by read_only mode.

        Examples:
            >>> sd = DH5({"key1": "value1", "key2": "value2"})
            >>> sd.lock_data()
            >>> sd.unlock_data('key2')
            >>> sd['key2'] = 5
            >>> sd['key1'] = 2
            ReadOnlyKeyError: "Cannot change a read-only key 'key1'."

        """
        if self._read_only is True:
            raise ValueError("Cannot unlock is global read_only mode was set to True")
        if isinstance(self._read_only, set):
            if remove_keys is None:
                self._read_only = False
            else:
                if isinstance(remove_keys, str):
                    remove_keys = (remove_keys,)
                for key in remove_keys:
                    if key in self._read_only:
                        self._read_only.remove(key)

        self._clean_precalculated_results()
        return self

    def _clean_precalculated_results(self):
        self._repr = None

    def __add_key(self, key):
        self._pre_save()
        self._keys.add(key)
        self._last_update.add(key)

    def __del_key(self, key):
        self._keys.remove(key)
        self._last_update.add(key)

    def __check_read_only_true(self, key):
        """Return true if data with this key is only available for read.

        Takes into account the external constrains.
        """
        return (self._read_only) and (self._read_only is True or key in self._read_only)

    @editing
    def update(
        self: _SELF, __m: Optional[dict] = None, **kwds: "DICT_OR_LIST_LIKE"
    ) -> _SELF:
        """Update data from a dictionary or keyword arguments.

        See `DH5.data_transformation` to learn more
            about how the types are converted.

        Args:
            __m (dict | None): A dictionary of key-value pairs to update the DH5 object with.
            **kwds (DICT_OR_LIST_LIKE): Keyword arguments of key-value pairs to update the DH5 object with.

        Returns:
            Self.

        Examples:
            >>> data = DH5()
            >>> data.update({'a': 1, 'b': 2})
            DH5({'a': 1, 'b': 2})
            >>> data.update(c=3, d=4)
            DH5({'a': 1, 'b': 2, 'c': 3, 'd': 4})

        """
        if __m is not None:
            kwds.update(__m)

        for key in kwds:  # pylint: disable=C0206
            if self.__check_read_only_true(key):
                raise ReadOnlyKeyError(key)
            self.__add_key(key)
            kwds[key] = transform_to_possible_formats(kwds[key])

        # self.pull(auto=True)
        self._data.update(**kwds)
        return self

    def _update(self, __m: Optional[dict] = None, **kwds: Any):
        """Update only internal data and attributes.

        Can be modified in read_only mode. Did not change a file.
        """
        if __m is not None:
            kwds.update(__m)

        for key in kwds:
            self._keys.add(key)
            self._unopened_keys.discard(key)

        self._data.update(kwds)

        return set(kwds.keys())

    @editing
    def pop(self, key: str) -> Union[Any, NotLoaded]:
        """Remove the specified key and return the value.

        Args:
            key (str): The key to remove.

        Returns:
            Same as `get` method, i.e. `DH5` if the value is a dict otherwise the value.
                If data was never loaded it will return `NotLoaded`. To load data use `get` method.

        Examples:
            >>> data = DH5({'a': 1, 'b': 2, 'c': 3})
            >>> data.pop('b')
            2

        """
        if self.__check_read_only_true(key):
            raise ReadOnlyKeyError(key, action="pop")
        self.__del_key(key)
        # self.pull(auto=True)
        if key not in self._unopened_keys:
            return self._data.pop(key)
        return NotLoaded()

    @editing
    def remove(self: _SELF, key: str) -> _SELF:
        """Remove the specified key and self.

        Args:
            key (str): The key to remove.

        Returns:
            Self.

        Examples:
            >>> data = DH5({'a': 1, 'b': 2, 'c': 3})
            >>> data.pop('b')
            DH5({'a': 1, 'c': 3})

        """
        self.pop(key)
        return self

    @overload
    def get_raw(self, __key: str) -> Any:
        """Return element as a dict. Return None if not found."""

    @overload
    def get_raw(self, __key: str, __default: _T) -> Union[Any, _T]:
        """With default value provided."""

    def get_raw(self, key: str, default: Any = None) -> Any:
        """Return raw value associated with the given key.

        Dictionaries are not converted to the `DH5` unlike `get` method.

        Args:
            key (str): Key to be searched.
            default (Any, optional): Value to be returned if the `key` is not found.
                The default value is `None`.


        Returns:
            Raw value without any conversion or the default value if the key is not found.

        Examples:
            >>> sync_data = DH5({'key1':{'a': 1, 'b': 2}, 'key2': 5})
            >>> sync_data.get_raw('key1')
            {'a': 1, 'b': 2}
            >>> sync_data.get_raw('key2')
            5
        """
        return self.__get_data__(key, default)

    @overload
    def get(self, __key: str) -> Any:
        """Return element as a DH5 class if it's dict. Return None if not found."""

    @overload
    def get(self, __key: str, __default: _T) -> Union[Any, _T]:
        """With default value provided."""

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve the value associated with the given key from the DH5 object.

        Args:
            key (str): Key to be searched.
            default (Any, optional): Value to be returned if the `key` is not found.
                The default value is `None`.

        Returns:
            The value associated with the key. If the value is a dict then it's converter
            into `DH5` object. This conversion take some time, but allow to change, save and
            this sub-object. For faster performance use `get_raw` method.

        Examples:
            >>> sync_data = DH5(filepath='data.json', data={'name': 'John', 'age': 30})
            >>> sync_data.get('name')
            'John'
            >>> sync_data.get('surname')
            None
            >>> sync_data.get('gender', 'unknown')
            'unknown' # Returns 'unknown' since 'gender' key doesn't exist

        """
        data = self.__get_data__(key, default)
        if isinstance(data, dict) and data:
            return DH5(
                filepath=self._filepath,
                data=data,
                overwrite=False,
                key_prefix=key,
                read_only=self.__check_read_only_true(key),
            )
        return data

    def __getitem__(self, __key: Union[str, tuple]) -> Any:
        """Return raw value associated with the given key.

        Same as `get_raw` but raises error if the key is not found.

        Args:
            key (str | tuple): The key to retrieve the dictionary for.

        Returns:
            Raw value without any conversion.

        Raises:
            KeyError: If the key is not found.

        """
        if isinstance(__key, tuple):
            if len(__key) > 1:
                return self.__getitem__(__key[0]).__getitem__(
                    __key[1:] if len(__key) > 2 else __key[1]
                )
            if len(__key) == 1:
                return self.__getitem__(__key[0])
            raise ValueError(
                "Key should be a string or tuple with at least one element"
            )
        return self.__get_data_or_raise__(__key)

    @editing
    def __setitem__(
        self, __key: Union[str, tuple], __value: "DICT_OR_LIST_LIKE"
    ) -> None:
        """Set value corresponding to the given key.

        See [`DH5.data_transformation`](data_transformation.md) to learn more
            about how the types are converted.

        Args:
            key (str | tuple): The key to retrieve the dictionary for.

        """
        if isinstance(__key, tuple):
            if not __key or len(__key) == 1 or len(__key) == 0:
                raise ValueError(
                    "Key should be a string or tuple with at least two elements"
                )

            self.__add_key(__key[0])
            if self.__check_read_only_true(__key[0]):
                raise ReadOnlyKeyError(__key[0], action="set")
            return self.__getitem__(__key[0]).__setitem__(
                __key[1:] if len(__key) > 2 else __key[1], __value  # type: ignore
            )

        if self.__check_read_only_true(__key):
            raise ReadOnlyKeyError(__key, action="set")

        self.__add_key(__key)
        __value = transform_to_possible_formats(__value)

        if self._read_only is not True:
            if hasattr(__value, "save"):
                self._classes_should_be_saved_internally.add(__key)

            if hasattr(__value, "__init__filepath__") and self._filepath:
                key = (
                    __key if self._key_prefix is None else f"{self._key_prefix}/{__key}"
                )
                __value.__init__filepath__(  # type: ignore
                    filepath=self._filepath,
                    filekey=key,
                    save_on_edit=self._save_on_edit,
                )

            if hasattr(__value, "__post__init__"):
                __value.__post__init__()  # type: ignore

        self.__set_data__(__key, __value)
        return None

    def __delitem__(self, key: str):
        self.pop(key)

    def __getattr__(self, __name: str):
        """Call if __getattribute__ does not work."""
        if (
            len(__name) > 1
            and __name[0] == "i"
            and __name[1:].isdigit()
            and __name not in self
        ):
            __name = __name[1:]
        if __name in self:
            data = self.get(__name)
            # if isinstance(data, dict) and data:
            #     return DH5(filepath=self._filepath, data=data, key_prefix=__name)
            return data
        raise AttributeError(f"No attribute {__name} found in DH5")

    def __setattr__(self, __name: str, __value: "DICT_OR_LIST_LIKE") -> None:
        """Call every time you set an attribute."""
        if __name.startswith("_"):
            return object.__setattr__(self, __name, __value)

        if isinstance(vars(self.__class__).get(__name), property):
            return object.__setattr__(self, __name, __value)
        return self.__setitem__(__name, __value)

    def __delattr__(self, __name: str) -> None:
        if __name in self:
            return self.__delitem__(__name)
        return object.__delattr__(self, __name)

    @overload
    def __get_data__(self, __key: str) -> Optional[None]:
        """Return None if the data doesn't contain key."""

    @overload
    def __get_data__(self, __key: str, __default: _T) -> Union[Any, _T]:
        """Return default value if the data doesn't contain key."""

    def __get_data__(self, __key: str, __default: Any = None):
        if __key in self._unopened_keys:
            self._load_from_h5(key=__key)
        data = self._data.get(__key, __default)
        if isinstance(data, NotLoaded):
            self._load_from_h5(key=__key)
            data = self._data.get(__key, __default)
        if self.__check_read_only_true(__key):
            if hasattr(data, "_read_only"):
                data._read_only = True  # type: ignore # pylint: disable=protected-access
            else:
                data = deepcopy(data)
        return data

    def __get_data_or_raise__(self, __key):
        # self.pull(auto=True)
        if __key in self._unopened_keys:
            self._load_from_h5(key=__key)
        data = self._data.__getitem__(__key)
        if isinstance(data, NotLoaded):
            self._load_from_h5(key=__key)
            data = self._data.__getitem__(__key)
        if self.__check_read_only_true(__key):
            if hasattr(data, "_read_only"):
                data._read_only = True  # type: ignore # pylint: disable=protected-access
            else:
                data = deepcopy(data)
        return data

    def __set_data__(self, __key: str, __value):
        # self.pull(auto=True)
        return self._data.__setitem__(__key, __value)

    def items(self):
        """Return all items in the collection.

        It opens all items that were not opened yet and return dictionary iterator.
        """
        if self._unopened_keys:
            self._load_from_h5(key=self._unopened_keys)
        return self._data.items()

    def values(self):
        """Return all values in the collection.

        It opens all items that were not opened yet and return dictionary iterator.
        """
        # self.pull(auto=True)
        if self._unopened_keys:
            self._load_from_h5(key=self._unopened_keys)
        return self._data.values()

    def keys(self) -> Set[str]:
        """Return all keys in the collection."""
        # self.pull(auto=True)
        return self._keys.copy().union(self._unopened_keys.copy())

    def keys_tree(self) -> Dict[str, Optional[dict]]:
        """Return dict of the keys, where value always is a dict or None.

        Examples:
            ```
            >>> sd = DH5({'a': {'b': 'value'}, 'c'})
            >>> sd.keys_tree()
            {'a': {'b': None}, 'c': None}
            ```

        For all unopened keys, it does not open them and does not explore the structure.
        """
        structure = get_keys_structure(self._data)

        for key in self._unopened_keys:
            structure[key] = None
        return structure

    def __iter__(self):
        return iter(self.keys())

    def _get_repr(self):
        if self._repr is None:
            additional_info = (
                {key: " (r)" for key in self._read_only}
                if isinstance(self._read_only, set)
                else None
            )
            self._repr = output_dict_structure(
                self._data, additional_info=additional_info
            ) + (
                f"\nUnloaded keys: {self._unopened_keys}" if self._unopened_keys else ""
            )

    def __repr__(self):
        self._get_repr()

        not_saved = (
            "" if self._last_data_saved or self._read_only is True else " (not saved)"
        )
        mode = (
            "r"
            if self._read_only is True
            else "w"
            if self._read_only is False
            else "rw"
        )
        mode = "l" if self._filepath is None and self._read_only is not True else mode
        not_saved = "" if mode == "l" else not_saved

        return f"{type(self).__name__} ({mode}){not_saved}: \n {self._repr}"

    def __str__(self):
        return self.__repr__()

    def __contains__(self, item):
        return (item in self._data) or (item in self._unopened_keys)

    def __dir__(self) -> Iterable[str]:
        return list(self._keys) + self._default_attr

    def __similar__(self, other: "DH5") -> bool:
        """Check if 2 DH5 are similar.

        It means: same file, mode, save_on_edit. Does not check the data.
        """
        return (
            self._filepath == other._filepath  # pylint: disable=protected-access
            and self._read_only == other._read_only  # pylint: disable=protected-access
            and self._save_on_edit
            == other._save_on_edit  # pylint: disable=protected-access
            and self.__should_initialized
            == other.__should_initialized  # pylint: disable=protected-access
        )

    def _pre_save(self, *args, **kwargs):
        del args, kwargs
        if self.__should_initialized and self._filepath:
            os.remove(self._filepath)
            self.__should_initialized = False

    def save(
        self,
        only_update: Union[bool, Iterable[str]] = True,
        filepath: Optional[str] = None,
        force: Optional[bool] = None,
    ):
        """Save the data to a file.

        Args:
            only_update (Union[bool, Iterable[str]], optional): Determines whether to save only
                the updated data or all data.
                If True, only the updated data will be saved. If False, all data will be saved.
                If an iterable of strings is provided, only the specified keys will be saved. Defaults to True.
            filepath (str, optional): The path to the file where the data will be saved.
                If not provided, the default filepath will be used. Defaults to None.
            force (bool, optional): Determines whether to force the save operation, even if only_update is True.
                If True, the save operation will be forced. If False or None, the save operation
                will be performed according to the value of only_update. Defaults to None.

        Returns:
            self

        Raises:
            ValueError: If the file is opened in read-only mode, it cannot be saved.
                The file should be reopened in write mode before saving.
        """
        if self._read_only is True:
            raise ValueError(
                "Cannot save opened in a read-only mode. Should reopen the file"
            )

        self._pre_save()

        if force is True or filepath is not None:
            only_update = False

        if isinstance(only_update, Iterable):
            last_update = self._last_update.intersection(only_update)
            self._last_update = self._last_update.difference(only_update)
        else:
            last_update, self._last_update = self._last_update, set()

        if len(self._last_update) == 0:
            self._last_data_saved = True

        filepath = self._check_if_filepath_was_set(filepath, self._filepath)

        if only_update is False:
            if self._read_only is False:
                data_to_save = self._data
            else:
                data_to_save = {
                    key: value
                    for key, value in self._data.items()
                    if key not in self._read_only or key in last_update
                }
            data_to_save.update(
                {
                    key: None
                    for key in last_update
                    if (key not in self._data) and not self.__check_read_only_true(key)
                }
            )

            self.__h5py_utils_save_dict_with_retry(filepath=filepath, data=data_to_save)

            return self

        for key in last_update:
            if key in self._classes_should_be_saved_internally:
                obj = self._data[key]
                if hasattr(obj, "save"):
                    self._data[key].save(only_update=only_update)
                else:
                    self._classes_should_be_saved_internally.remove(key)

        self.__h5py_utils_save_dict_with_retry(
            filepath=filepath,
            data={
                key: self._data.get(key)
                for key in last_update
                if key not in self._classes_should_be_saved_internally
            },
        )

        return self

    def __h5py_utils_save_dict_with_retry(self, filepath: str, data: dict):
        # print("open", time.time(), self._raise_file_locked_error)
        for i in range(self._retry_on_file_locked_error):
            try:
                # print("_raise_file_locked_error", self._raise_file_locked_error, list(data.keys()))
                self._file_modified_time = h5py_utils.save_dict(
                    filename=filepath + ".h5", data=data, key_prefix=self._key_prefix
                )
                return
            except h5py_utils.FileLockedError as error:
                if self._raise_file_locked_error:
                    raise error
                logging.info("File is locked. waiting 2s and %d more retrying.", i)
                from ..utils import async_utils

                async_utils.sleep(1)

        raise h5py_utils.FileLockedError(
            f"Even after {self._retry_on_file_locked_error} data was not saved"
        )

    @staticmethod
    def _check_if_filepath_was_set(
        filepath: Optional[str], filepath2: Optional[str]
    ) -> str:
        """Return path to the file with filename, but without extension."""
        filepath = filepath or filepath2
        if filepath is None:
            raise ValueError(
                "Should provide filepath or set self.filepath before saving"
            )
        filepath = (
            (filepath.rsplit(".h5", 1)[0]) if filepath.endswith(".h5") else filepath
        )
        return filepath

    @property
    def filepath(self):
        """Return the filepath without the '.h5' extension.

        If the filepath is None, returns None.
        """
        return None if self._filepath is None else (self._filepath.rsplit(".h5", 1)[0])

    @filepath.setter
    def filepath(self, value: str):
        if not isinstance(value, str):
            value = str(value)
        self._filepath = value if value.endswith(".h5") else value + ".h5"

    @property
    def filename(self) -> Optional[str]:
        """Return the filename of the current filepath without '.h5' extension.

        Returns:
            Optional[str]: The filename of the current filepath, or None if the filepath is None.
        """
        filepath = self.filepath
        if filepath is None:
            return None
        return os.path.basename(filepath)

    @property
    def save_on_edit(self):
        """Return the current value of the save_on_edit attribute."""
        return self._save_on_edit

    def asdict(self):
        """Return the internal data of the object as a dictionary.

        Returns:
            dict: A dictionary representation of the object's internal data.
        """
        return self._data

    def pull_available(self):
        """Check if the file has been modified elsewhere since the last save.

        Raises:
            ValueError: If the filepath has not been set.

        Returns:
            bool: True if the file has been modified, False otherwise.
        """
        if self.filepath is None:
            raise ValueError("Cannot pull from file if it's not been set")
        file_modified = os.path.getmtime(self.filepath + ".h5")
        return self._file_modified_time != file_modified

    def pull(self, force_pull: bool = False):
        """Pull data from a file and reloads it into the object.

        Args:
            force_pull (bool, optional): If True, forces to update data even if the file
            has not been modified. Defaults to False.

        Raises:
            ValueError: If the filepath has not been set.

        Returns:
            self: The updated object.
        """
        if self.filepath is None:
            raise ValueError("Cannot pull from file if it's not been set")

        if force_pull or self.pull_available():
            logging.debug("File modified so it will be reloaded.")
            self._data = {}
            self._keys = set()
            self._clean_precalculated_results()
            self._load_from_h5()

        return self

    @overload
    def close_data(self, key: None = None, every: Literal[True] = True):
        """Close every opened key so it could be collected by the garbage collector afterwards."""

    @overload
    def close_data(self, key: Iterable[str]):
        """Close every key provided so it could be collected by the garbage collector afterwards."""

    @overload
    def close_data(self, key: str):  # type: ignore
        """Close the key so it could be collected by the garbage collector afterwards."""

    def close_data(
        self,
        key: Optional[Union[str, Iterable[str]]] = None,
        every: Optional[Literal[True]] = None,
    ):
        """Close the key so it could be collected by the garbage collector afterwards.

        Args:
            key (str | Iterable[str], optional): key or keys that should be closed. Defaults to None.
            every (True, optional): put to True if all keys should be closed. Defaults to None.

        Raises:
            ValueError: if both key and every are not provided.

        Returns:
            Self.
        """
        if every is True:
            for k in self.keys():
                self.close_data(k)
            return self
        elif key is None:
            raise ValueError("Should provide key or every=True.")

        if not isinstance(key, str):
            for k in key:
                self.close_data(k)
            return self

        if key not in self._unopened_keys:
            self._data.pop(key)
        self._unopened_keys.add(key)

        return self
