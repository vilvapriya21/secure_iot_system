"""
System configuration singleton.

This module defines a singleton configuration class
that provides global, immutable settings for the
IoT anomaly detection system.
"""


class SystemConfig:
    """
    Singleton class for system-wide configuration.

    Ensures that only one configuration instance
    exists throughout the application lifecycle.
    """

    _instance = None
    _frozen = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """
        Initialize configuration values once.
        """
        if self._frozen:
            return

        # Core system settings
        self.buffer_size = 100
        self.max_sensors = 50
        self.anomaly_threshold = 2.5
        self.poll_interval = 0.5  # seconds

        # Freeze configuration after initialization
        self._frozen = True

    def __setattr__(self, key, value):
        """
        Prevent modification of configuration
        after initialization.
        """
        if getattr(self, "_frozen", False):
            raise AttributeError("SystemConfig is immutable.")
        super().__setattr__(key, value)