"""This module contains asynchronous functions."""
import threading


def sleep(delay):
    """Sleep for the specified delay in seconds.

    Args:
        delay (float): The delay in seconds.

    """
    event = threading.Event()
    event.wait(delay)
    event.clear()
