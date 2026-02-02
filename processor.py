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
        end = time.perf_counter()
        return result, end - start

    return wrapper


# ---------------- Sensor Cache ---------------- #

class SensorCache:
    """
    Weak reference cache for active sensors.
    """

    def __init__(self) -> None:
        self._cache: weakref.WeakValueDictionary[str, Sensor] = (
            weakref.WeakValueDictionary()
        )

    def add(self, sensor: Sensor) -> None:
        self._cache[sensor.name] = sensor

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

    @profile_execution
    def process_batch(self) -> Tuple[float, float]:
        """
        Process buffered data using NumPy vectorization.

        Returns:
            (moving_average, standard_deviation)
        """
        data = np.array(self._buffer, dtype=np.float64)

        moving_avg = data.mean()
        std_dev = data.std()

        self._buffer.clear()
        return moving_avg, std_dev