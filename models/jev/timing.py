"""The timed decorator prints how long a synchronous function takes while preserving its return value.
It also exposes the latest duration through elapsed_ms and prints timing even if the function raises an error.
Only work inside the decorated function is measured, including any connection setup during an API request.
"""

from functools import wraps
from time import perf_counter


def timed(function):
    """Print latency and expose the latest duration as wrapper.elapsed_ms."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            wrapper.elapsed_ms = (perf_counter() - start) * 1000
            print(f"{function.__name__}: {wrapper.elapsed_ms:.1f} ms")

    wrapper.elapsed_ms = None
    return wrapper
