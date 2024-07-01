"""Random utilities for the dh5 package."""

from typing import TYPE_CHECKING, Optional, Tuple, Union

if TYPE_CHECKING:
    from pathlib import Path  # pragma: no cover


def get_timestamp() -> str:
    """Get the current timestamp in the format 'YYYY_MM_DD__HH_MM_SS'.

    Returns:
        str: The current timestamp.
    """
    import datetime

    x = datetime.datetime.now()
    return x.strftime("%Y_%m_%d__%H_%M_%S")


def lstrip_int(line: str) -> Optional[Tuple[str, str, str]]:
    """Find whether timestamp ends.
    Returns timestamp and rest of the line, if possible.

    Args:
        line (str): The line to check for a timestamp.

    Returns:
        Optional[Tuple[str, str, str]]: A tuple containing the prefix, main part, and suffix
            of the line if a timestamp is found, None otherwise.
    """
    import re

    main = re.search("_[A-Za-z]", line)
    if main is None:
        return None
    prefix, main = line[: main.start()], line[main.start() + 1 :]
    if "__" in main:
        suffix_index = main.rfind("__")
        suffix = main[suffix_index + 2 :]
        if suffix.isdecimal():
            main = main[:suffix_index]
        else:
            suffix = ""
    else:
        suffix = ""

    if not prefix.replace("_", "").replace("-", "").isdigit():
        return None

    return prefix.strip("_"), main, suffix


def get_path_from_filename(filename: Union[str, "Path"]) -> Union[str, tuple]:
    """Given a filename, returns the path to the file.

    If the filename contains a path, returns the filename as is.
    If the filename ends with '.h5', removes the extension.
    If the filename starts with a timestamp, returns a tuple with (the suffix that does after
    the timestamp, the full filename without '.h5' extension in the end).

    Args:
        filename (Union[str, "Path"]): The filename to get the path from.

    Returns:
        Union[str, tuple]: The path to the file as tuple (folder, filename) or the filename itself.
        Return directly filename if it contains a slash, therefore represents the path.
    """
    filename = str(filename)

    if "/" in filename or "\\" in filename:
        return filename

    filename = filename[:-3] if filename.endswith(".h5") else filename

    name_with_prefix = lstrip_int(filename)

    if name_with_prefix:
        suffix = name_with_prefix[1]
        return (suffix, filename)
    return filename
