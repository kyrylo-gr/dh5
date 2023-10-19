class NotLoaded:
    """Data that has not been loaded yet."""

    def __init__(self):
        pass

    def __str__(self) -> str:
        return """This key is not loaded. If you see this message,
                it means that you accessed the key not via DH5 object"""

    def __repr__(self) -> str:
        return """This key is not loaded"""
