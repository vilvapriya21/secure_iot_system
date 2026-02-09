"""
Sensor base class and simulated sensor implementations.
"""

import abc
import asyncio
import random
from collections.abc import Generator
from registry import SensorRegistryMeta


class Sensor(abc.ABC, metaclass=SensorRegistryMeta):
    """
    Base class for all sensor types.

    Defines the contract for asynchronous data reading
    and calibration behavior.
    """

    def __init__(self, name: str) -> None:
        """
        Initialize the sensor with its logical name.

        Args:
            name (str): Human-readable sensor name.
        """
        self.name = name
        self._calibrated = False
        self._stream: Generator[float, None, None] = self._sensor_stream()

    @abc.abstractmethod
    async def read_data(self) -> float:
        """Read one sensor value asynchronously."""
        raise NotImplementedError

    @abc.abstractmethod
    def calibrate(self) -> None:
        """Perform sensor calibration."""
        raise NotImplementedError

    @property
    def is_calibrated(self) -> bool:
        """Whether the sensor has been calibrated."""
        return self._calibrated

    def _ensure_calibrated(self) -> None:
        """
        Ensure the sensor has been calibrated before use.

        Raises:
            RuntimeError: If the sensor is not calibrated.
        """
        if not self._calibrated:
            raise RuntimeError(
                f"{self.__class__.__name__} must be calibrated "
                "before reading data."
            )

    def _sensor_stream(self) -> Generator[float, None, None]:
        """
        Yield an infinite stream of simulated readings.

        Yields:
            float: Random sensor value.
        """
        while True:
            yield random.uniform(0.0, 100.0)

    async def _safe_read(self) -> float:
        """
        Safely read from the sensor stream with edge-case handling.

        Returns:
            float: Valid sensor reading or safe fallback value.
        """
        try:
            value = next(self._stream)

            if value is None or not isinstance(value, (int, float)):
                raise ValueError("Invalid sensor reading")

            return float(value)

        except StopIteration:
            # Stream unexpectedly exhausted
            return 0.0

        except Exception as exc:
            # Catch-all to avoid crashing async pipeline
            print(f"[{self.__class__.__name__} Error] {exc}")
            return 0.0


class TempSensor(Sensor):
    """Temperature sensor implementation."""

    SENSOR_NAME = "temperature"

    def __init__(self) -> None:
        super().__init__("Temperature")

    async def read_data(self) -> float:
        self._ensure_calibrated()
        await asyncio.sleep(random.uniform(0.01, 0.05))
        return await self._safe_read()

    def calibrate(self) -> None:
        self._calibrated = True


class PressureSensor(Sensor):
    """Pressure sensor implementation."""

    SENSOR_NAME = "pressure"

    def __init__(self) -> None:
        super().__init__("Pressure")

    async def read_data(self) -> float:
        self._ensure_calibrated()
        await asyncio.sleep(random.uniform(0.01, 0.05))
        return await self._safe_read()

    def calibrate(self) -> None:
        self._calibrated = True


class VibrationSensor(Sensor):
    """Vibration sensor implementation."""

    SENSOR_NAME = "vibration"

    def __init__(self) -> None:
        super().__init__("Vibration")

    async def read_data(self) -> float:
        self._ensure_calibrated()
        await asyncio.sleep(random.uniform(0.01, 0.05))
        return await self._safe_read()

    def calibrate(self) -> None:
        self._calibrated = True
