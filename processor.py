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

import numpy as np

from sensor import Sensor


# ---------------- Profiling Decorator ---------------- #

def profile_execution(func):
    """
    Decorator to measure execution time of a function.
    """

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed

    return wrapper


# ---------------- Sensor Cache ---------------- #

class SensorCache:
    """
    Weak reference cache for active sensors.
    Uses object id to avoid name collisions.
    """

    def __init__(self) -> None:
        self._cache: weakref.WeakValueDictionary[int, Sensor] = (
            weakref.WeakValueDictionary()
        )

    def add(self, sensor: Sensor) -> None:
        self._cache[id(sensor)] = sensor

    def size(self) -> int:
        return len(self._cache)

    def force_gc(self) -> int:
        gc.collect()
        return len(self._cache)


# ---------------- Data Processor ---------------- #

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

        Returns True when batch is ready.
        """
        self._buffer.append(value)
        return len(self._buffer) >= self.batch_size

    # -------- Slow Python Implementation (Baseline) -------- #

    @staticmethod
    def slow_python_stats(values: List[float]) -> Tuple[float, float]:
        """
        Intentionally slow loop-based statistics
        for profiling comparison.
        """
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return mean, variance ** 0.5

    # -------- Optimized NumPy Implementation -------- #

    @profile_execution
    def process_batch(self) -> Tuple[float, float]:
        """
        Process buffered data using NumPy vectorization.

        Returns:
            (mean, standard_deviation)
        """
        data = np.array(self._buffer, dtype=np.float64)

        mean = data.mean()
        std = data.std()

        self._buffer.clear()
        return mean, std