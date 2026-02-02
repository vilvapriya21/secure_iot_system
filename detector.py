"""
Anomaly detection strategies and controller.

This module implements the Strategy design pattern
to allow interchangeable anomaly detection algorithms.
"""

import abc
import numpy as np
from typing import Iterable


class DetectionStrategy(abc.ABC):
    """
    Abstract base class for anomaly detection strategies.
    """

    @abc.abstractmethod
    def detect(self, data: Iterable[float]) -> bool:
        """
        Analyze data and determine if an anomaly exists.
        """
        raise NotImplementedError


class ZScoreStrategy(DetectionStrategy):
    """
    Detect anomalies using Z-score statistical method.
    """

    def __init__(self, threshold: float = 2.5) -> None:
        self.threshold = threshold

    def detect(self, data: Iterable[float]) -> bool:
        values = np.array(list(data))

        if values.size == 0:
            return False

        std = values.std()
        if std == 0:
            return False

        mean = values.mean()
        z_scores = np.abs((values - mean) / std)
        return np.any(z_scores > self.threshold)


class ThresholdStrategy(DetectionStrategy):
    """
    Detect anomalies using fixed upper/lower bounds.
    """

    def __init__(self, min_value: float, max_value: float) -> None:
        self.min_value = min_value
        self.max_value = max_value

    def detect(self, data: Iterable[float]) -> bool:
        values = np.array(list(data))

        if values.size == 0:
            return False

        return np.any(
            (values < self.min_value) | (values > self.max_value)
        )


class AnomalyDetector:
    """
    Context class that uses a detection strategy.
    """

    def __init__(self, strategy: DetectionStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: DetectionStrategy) -> None:
        """Replace the current detection strategy."""
        self._strategy = strategy

    def detect(self, data: Iterable[float]) -> bool:
        """Detect anomaly using the active strategy."""
        return self._strategy.detect(data)