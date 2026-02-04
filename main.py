"""
Main entry point for the Secure IoT Anomaly Detection System.

Responsibilities:
- Build sensors using Factory
- Run async sensor data collection
- Process data in NumPy batches
- Detect anomalies via Strategy pattern
- Secure alerts with hashing + encryption
"""

import asyncio
import logging

from factory import SensorFactory
from config import SystemConfig
from detector import AnomalyDetector, ZScoreStrategy
from data_engine import sensor_loop
from processor import DataProcessor, SensorCache
from security import (
    compute_sha256,
    encrypt_alert,
    decrypt_alert,
    generate_key,
    save_secure_log,
)

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def build_sensors(count: int):
    """Create sensors using Factory pattern."""
    sensor_types = ["temperature", "pressure", "vibration"]
    sensors = []

    for i in range(count):
        sensor = SensorFactory.create_sensor(sensor_types[i % 3])
        sensor.calibrate()
        sensors.append(sensor)

    logger.info("Built and calibrated %d sensors", count)
    return sensors


async def run_system():
    config = SystemConfig()
    logger.info(
        "Starting system | sensors=%d | buffer=%d",
        config.max_sensors,
        config.buffer_size,
    )

    # WeakRef cache
    cache = SensorCache()

    # Create sensors
    sensors = build_sensors(config.max_sensors)
    for s in sensors:
        cache.add(s)

    logger.info("Sensors added to weak reference cache")

    # Processing & detection
    processor = DataProcessor(batch_size=config.buffer_size)
    detector = AnomalyDetector(
        strategy=ZScoreStrategy(threshold=config.anomaly_threshold)
    )

    # Security
    key = generate_key()
    logger.info("Security key generated")

    # Async data collection
    logger.info("Starting async sensor data collection")
    snapshots = await sensor_loop(sensors, iterations=10)

    for snapshot in snapshots:
        for value in snapshot.values():
            batch_ready = processor.add_reading(value)

        if batch_ready:
            (mean, std), elapsed = processor.process_batch()

            data_str = ",".join(f"{v:.2f}" for v in snapshot.values())
            data_hash = compute_sha256(data_str.encode())

            logger.info(
                "Batch processed | mean=%.2f | std=%.2f | time=%.6fs",
                mean,
                std,
                elapsed,
            )

            # Keep prints for assessment proof
            print(f"Integrity hash: {data_hash}")

            if detector.detect(snapshot.values()):
                alert = f"Anomaly detected | mean={mean:.2f}, std={std:.2f}"
                encrypted = encrypt_alert(alert, key)
                save_secure_log("alerts.log", encrypted)

                logger.warning("Anomaly detected and encrypted alert stored")

                # Verification proof
                decrypted = decrypt_alert(encrypted, key)
                print("Decrypted alert check:", decrypted)

    # WeakRef demonstration
    logger.info("Sensors before GC: %d", cache.size())
    del sensors
    logger.info("Sensors after GC: %d", cache.force_gc())

    logger.info("System execution completed successfully")


def main():
    asyncio.run(run_system())


if __name__ == "__main__":
    main()
