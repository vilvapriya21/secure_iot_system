"""
Sensor registry metaclass.

This module provides a metaclass that automatically
registers all concrete Sensor implementations
at class creation time.
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
            SensorRegistryMeta._registry[name] = cls
    
        return cls

    @classmethod
    def get_registry(mcls) -> Dict[str, Type]:
        """
        Return the sensor class registry.

        Returns:
            Dictionary mapping class names to sensor classes.
        """
        return dict(mcls._registry)