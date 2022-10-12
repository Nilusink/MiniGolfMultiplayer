"""
core/debug.py

Debugging functions

Authors: MelonenBuby
Date:   07.07.2022
"""

################################################################################
#                                Import modules                                #
################################################################################

from typing import Callable
from time import perf_counter_ns


################################################################################
#                               Debug functions                                #
################################################################################


def all_callables(decorator, **kwargs) -> callable:
    """
    Adds a decorator on all callables of a class

    :param decorator: Decorator for the funtions
    :param kwargs: Keywordargs for the decorator
    """
    def decorate(cls):
        """
        Modifies the class (adds the decorators)

        :param cls: The class (set automatically)
        :return: returns the modified class
        """
        for attr in cls.__dict__:  # Goes through all of the class __dict__
            if callable(getattr(cls, attr)):  # Filter for callables (functions)
                setattr(cls, attr, decorator(getattr(cls, attr), **kwargs))  # Add the decorator with the kwargs
        return cls

    return decorate


def debug(func: Callable, debugvar_name: str | None = "debug_mode", min_debug: int | None = 3) -> Callable:
    """
    Debug decorator for functions in classes
    All Params are set by the all_callables function

    :param func: Callable (function)
    :param debugvar_name: Class variable-name of the debug mode
    :param min_debug: minimum the debugvar have to be for debugprints
    """

    def wrapper(*args, **kwargs) -> any:
        """
        Calls the function surrounded with some debugging

        :param args: Arguments that are given
        :param kwargs: Keywordarguments that are given
        :return: Anything the function returns
        """
        debug_mode: int = 0
        time_start: float = 0.0

        try:
            debug_mode = args[0].__dict__[debugvar_name]
        except KeyError:
            pass

        if debug_mode >= min_debug:
            time_start = perf_counter_ns()
            print(f"BEGINN: {func} with args {args} with kwargs {kwargs}")

        returns = func(*args, **kwargs)

        if debug_mode >= min_debug:
            print(f"END: {func} in {(perf_counter_ns()-time_start)/10**6}ms with return {returns}")

        return returns
    return wrapper
