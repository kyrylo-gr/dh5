"""Internal classes for DH5."""


class NotLoaded:
    """Data that has not been loaded yet."""

    def __init__(self):
        """Nothing to do."""

    def __str__(self) -> str:
        return """This key is not loaded. If you see this message,
                it means that you accessed the key not via DH5 object"""  # pragma: no cover

    def __repr__(self) -> str:
        return """This key is not loaded"""  # pragma: no cover
