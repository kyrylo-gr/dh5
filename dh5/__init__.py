# flake8: noqa: F401 # pylint: disable=E0401
import typing as _t
from copy import deepcopy as _deepcopy

from . import dh5_types
from .__config__ import __version__
from .dh5_class import DH5

if _t.TYPE_CHECKING:
    from pathlib import Path  # pragma: no cover


def load(
    filepath_or_data: _t.Optional[_t.Union[str, dict, "Path"]] = None,
    /,
    mode: _t.Optional[_t.Literal["r", "w", "a", "w=", "a="]] = None,
    *,
    filepath: _t.Optional[_t.Union[str, "Path"]] = None,
    save_on_edit: bool = False,
    overwrite: _t.Optional[bool] = None,
    data: _t.Optional[dict] = None,
    open_on_init: _t.Optional[bool] = None,
    **kwds,
):
    """Open H5 file in read/write mode.


    Args:
        filepath_or_data (str|dict, optional): either filepath, either data as dict.
        filepath (str|Path, optional): filepath to load. Defaults to None.
        save_on_edit (bool, optional): Save data as soon as you changed it.
            Defaults to False. And data should be saved using `save()` method.
        overwrite: If file exists, overwrite it. Defaults to raise error is file exist.
        data (Optional[dict], optional):
            Data to load. If data provided, file . Defaults to None.
        open_on_init (Optional[bool], optional): open_on_init. Defaults to True.

    """
    return DH5(
        filepath_or_data,
        mode=mode,
        filepath=filepath,
        save_on_edit=save_on_edit,
        data=data,
        open_on_init=open_on_init,
        overwrite=overwrite,
        **kwds,
    )


def save(
    data: dict,
    filepath: str,
    mode: _t.Literal["w", "a"] = "w",
    overwrite: _t.Optional[bool] = None,
    **kwds,
):
    """Save data to H5 file.

    Args:
        filepath (str): The path to the H5 file.
        data (dict): The data to be saved.
        **kwds: Additional keyword arguments to be passed to the DH5 constructor.

    Returns:
        DH5: DH5 object with data.
    """
    dh5 = DH5(
        data=_deepcopy(data), **kwds, filepath=filepath, overwrite=overwrite, mode=mode
    )
    return dh5.save(filepath=filepath)
