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


def all_methods(decorator, **kwargs) -> callable:
    """
    Decorate all callables in a class

    :param decorator: Decorator for the funtions
    :param kwargs: Keywordargs for the decorator
    """
    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr), **kwargs))
        return cls

    return decorate


def debug(func: Callable, debugvar_name: str | None = "debug_mode", min_debug: int | None = 3) -> Callable:
    """
    Debug decorator for functions in classes

    For debug-prints the functions must have a variabe named debug_mode
    """
    def wrapper(*args, **kwargs) -> None:
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
