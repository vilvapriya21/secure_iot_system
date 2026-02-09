"""
Sensor registry metaclass to auto-register sensor implementations.
"""

import inspect
from typing import Dict, Type
from abc import ABCMeta


class SensorRegistryMeta(ABCMeta):
    """
    Metaclass that auto-registers concrete Sensor subclasses.

    Any non-abstract class created using this metaclass
    will be added to the central registry.
    """

    _registry: Dict[str, Type] = {}

    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)

        # Register only concrete (non-abstract) classes
        if not inspect.isabstract(cls):
            sensor_name = getattr(cls, "SENSOR_NAME", None)

            # Prefer logical sensor name if available
            key = sensor_name.lower() if sensor_name else name
            mcls._registry[key] = cls

        return cls

    @classmethod
    def get_registry(mcls) -> Dict[str, Type]:
        """
        Return the sensor class registry.

        Returns:
            Dictionary mapping sensor names to sensor classes.
        """
        return dict(mcls._registry)
