"""
Sensor factory implementation.

Creates sensor instances based on logical
sensor type strings using the SensorRegistryMeta registry.
"""

from sensor import Sensor
from registry import SensorRegistryMeta


class SensorFactory:
    """
    Factory for creating Sensor instances.

    Uses the SensorRegistryMeta registry to dynamically
    instantiate concrete sensor implementations.
    """

    @staticmethod
    def create_sensor(sensor_type: str) -> Sensor:
        """
        Create a sensor instance based on the given type.

        Args:
            sensor_type: Logical sensor type name (e.g., "temperature").

        Returns:
            An instance of a concrete Sensor subclass.

        Raises:
            ValueError: If the sensor type is unknown.
        """
        if not sensor_type or not sensor_type.strip():
            raise ValueError("Sensor type must be a non-empty string.")

        normalized = sensor_type.strip().lower()
        registry = SensorRegistryMeta.get_registry()

        if normalized not in registry:
            valid = ", ".join(registry.keys())
            raise ValueError(
                f"Unknown sensor type '{sensor_type}'. "
                f"Available sensors: {valid}"
            )

        return registry[normalized]()