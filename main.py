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

from factory import SensorFactory
from config import SystemConfig
from detector import AnomalyDetector, ZScoreStrategy
from data_engine import sensor_loop
from processor import DataProcessor, SensorCache
from security import compute_sha256, encrypt_alert, decrypt_alert, generate_key, save_secure_log


def build_sensors(count: int):
    """Create sensors using Factory pattern."""
    sensor_types = ["temperature", "pressure", "vibration"]
    sensors = []

    for i in range(count):
        sensor = SensorFactory.create_sensor(sensor_types[i % 3])
        sensor.calibrate()
        sensors.append(sensor)

    return sensors


async def run_system():
    config = SystemConfig()
    print(f"Starting system | sensors={config.max_sensors}, buffer={config.buffer_size}")

    # WeakRef cache
    cache = SensorCache()

    # Create sensors
    sensors = build_sensors(config.max_sensors)
    for s in sensors:
        cache.add(s)

    # Processing & detection
    processor = DataProcessor(batch_size=config.buffer_size)
    detector = AnomalyDetector(
        strategy=ZScoreStrategy(threshold=config.anomaly_threshold)
    )

    # Security
    key = generate_key()

    # Async data collection
    snapshots = await sensor_loop(sensors, iterations=10)

    for snapshot in snapshots:
        for value in snapshot.values():
            batch_ready = processor.add_reading(value)

        if batch_ready:
            (mean, std), elapsed = processor.process_batch()

            data_str = ",".join(f"{v:.2f}" for v in snapshot.values())
            data_hash = compute_sha256(data_str.encode())

            print(f"Batch mean={mean:.2f}, std={std:.2f}, time={elapsed:.6f}s")
            print(f"Integrity hash: {data_hash}")

            if detector.detect(snapshot.values()):
                alert = f"Anomaly detected | mean={mean:.2f}, std={std:.2f}"
                encrypted = encrypt_alert(alert, key)
                save_secure_log("alerts.log", encrypted)

                # Verification
                decrypted = decrypt_alert(encrypted, key)
                print("Decrypted alert check:", decrypted)

    # WeakRef demonstration
    print("Sensors before GC:", cache.size())
    del sensors
    print("Sensors after GC:", cache.force_gc())

    print("System execution completed successfully.")


def main():
    asyncio.run(run_system())


if __name__ == "__main__":
    main()