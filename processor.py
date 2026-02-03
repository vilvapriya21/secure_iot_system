"""
Data processing and performance optimization module.

Handles buffering of sensor readings, NumPy-based
statistical analysis, weak reference caching, and
execution time profiling.
"""

import time
import weakref
import gc
from typing import List, Tuple
from functools import wraps

import numpy as np

from sensor import Sensor


# Profiling Decorator

def profile_execution(func):
    """
    Decorator to measure execution time of a function.

    Returns a tuple of (result, elapsed_time).
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed

    return wrapper


# Sensor Cache

class SensorCache:
    """
    Weak reference cache for active sensors.

    Uses object id as key to avoid name collisions
    and allow automatic garbage collection.
    """

    def __init__(self) -> None:
        self._cache: weakref.WeakValueDictionary[int, Sensor] = (
            weakref.WeakValueDictionary()
        )

    def add(self, sensor: Sensor) -> None:
        """Add a sensor to the weak reference cache."""
        self._cache[id(sensor)] = sensor

    def size(self) -> int:
        """Return the number of active cached sensors."""
        return len(self._cache)

    def force_gc(self) -> int:
        """
        Force garbage collection and return
        remaining cached sensor count.
        """
        gc.collect()
        return len(self._cache)


# Data Processor

class DataProcessor:
    """
    Processes sensor data batches using NumPy
    for efficient statistical analysis.
    """

    def __init__(self, batch_size: int = 100) -> None:
        self.batch_size = batch_size
        self._buffer: List[float] = []

    def add_reading(self, value: float) -> bool:
        """
        Add a sensor reading to the buffer.

        Returns:
            True if the batch size is reached.
        """
        self._buffer.append(value)
        return len(self._buffer) >= self.batch_size

    # Slow Python Implementation

    @staticmethod
    def slow_python_stats(values: List[float]) -> Tuple[float, float]:
        """
        Intentionally slow loop-based statistics
        for profiling comparison.

        Raises:
            ValueError: If values list is empty.
        """
        if not values:
            raise ValueError("Values list cannot be empty.")

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return mean, variance ** 0.5

    # Optimized NumPy Implementation

    @profile_execution
    def process_batch(self) -> Tuple[Tuple[float, float], float]:
        """
        Process buffered data using NumPy vectorization.

        Returns:
            ((mean, standard_deviation), execution_time)

        Raises:
            ValueError: If no data is available for processing.
        """
        if not self._buffer:
            raise ValueError("No data available to process.")

        data = np.array(self._buffer, dtype=np.float64)

        mean = data.mean()
        std = data.std()

        self._buffer.clear()
        return mean, std
