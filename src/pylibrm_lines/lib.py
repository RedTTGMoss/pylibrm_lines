"""
This module provides functions to configure LIB rm_lines directly.

While it does wrap the library implementations in a pythonic way,
it does not check for any errors or exceptions that may occur.
However, these are basic functions that shouldn't fail under normal circumstances.
"""

import ctypes

from rm_lines_sys import lib

def setDebugMode(debug: bool):
    """
    Set the debug mode for the library.
    This will enable both debug logging and debug rendering.

    :param debug: If True, enables debug mode; otherwise, disables it.
    """
    lib.setDebugMode(debug)

def getDebugMode() -> bool:
    """
    Check if the library is in debug mode.

    :return: True if debug mode is enabled, False otherwise.
    """
    return lib.getDebugMode()

def setLogger(func: callable):
    """
    Set a custom logging function for the library.

    :param func: A callable that takes a string message as an argument.
    """

    @ctypes.CFUNCTYPE(None, ctypes.c_char_p)
    def python_logger(msg):
        func(msg.decode('utf-8', errors='replace'))

    lib.setLogger(python_logger)

def setErrorLogger(func: callable):
    """
    Set a custom error logging function for the library.

    :param func: A callable that takes a string message as an argument.
    """

    @ctypes.CFUNCTYPE(None, ctypes.c_char_p)
    def python_logger(msg):
        func(msg.decode('utf-8', errors='replace'))

    lib.setErrorLogger(python_logger)

def setDebugLogger(func: callable):
    """
    Set a custom debug logging function for the library.
    Debug messages are verbose but are only triggered if debug mode is enabled.

    :param func: A callable that takes a string message as an argument.
    """

    @ctypes.CFUNCTYPE(None, ctypes.c_char_p)
    def python_logger(msg):
        func(msg.decode('utf-8', errors='replace'))

    lib.setDebugLogger(python_logger)