"""
Main entry point for the Secure IoT Anomaly Detection System.

Features:
- Builds 50 concurrent sensor instances
- Collects async data streams
- Processes data in batches using NumPy
- Detects anomalies via Strategy pattern
- SHA-256 hashes data for integrity
- Encrypts and logs alerts securely
- Demonstrates weakref sensor cache
- Profiles batch processing time and compares to slow Python loop
"""

import asyncio
import random
from typing import List

from sensor import TempSensor, PressureSensor, VibrationSensor, Sensor
from factory import SensorFactory
from config import SystemConfig
from detector import AnomalyDetector, ZScoreStrategy, ThresholdStrategy
from data_engine import sensor_loop
from processor import DataProcessor, SensorCache
from security import compute_sha256, encrypt_alert, decrypt_alert, generate_key, save_secure_log


# Build Sensor Instances
def build_sensors(num_sensors: int = 50) -> List[Sensor]:
    """
    Build a list of sensors for simulation.
    Cycles through Temp, Pressure, Vibration to reach desired count.
    """
    sensor_types = ["temperature", "pressure", "vibration"]
    sensors = []

    for i in range(num_sensors):
        sensor_type = sensor_types[i % len(sensor_types)]
        sensor = SensorFactory.create_sensor(sensor_type)
        sensor.calibrate()  # Calibrate before use
        sensors.append(sensor)

    return sensors


# Optional: Slow Python loop for profiling comparison
def slow_process(buffer_values):
    import time
    start = time.perf_counter()
    mean_slow = sum(buffer_values) / len(buffer_values)
    std_slow = (sum((x - mean_slow) ** 2 for x in buffer_values) / len(buffer_values)) ** 0.5
    end = time.perf_counter()
    return (mean_slow, std_slow), end - start


# Run Simulation
async def run_system():
    config = SystemConfig()
    print(f"Starting simulation with buffer_size={config.buffer_size}, "
          f"max_sensors={config.max_sensors}")

    # Sensor cache
    cache = SensorCache()

    # Build 50 sensors
    sensors = build_sensors(config.max_sensors)
    for sensor in sensors:
        cache.add(sensor)

    # Data processor and anomaly detector
    processor = DataProcessor(batch_size=config.buffer_size)
    zscore_strategy = ZScoreStrategy(threshold=config.anomaly_threshold)
    threshold_strategy = ThresholdStrategy(min_value=0.0, max_value=100.0)
    detector = AnomalyDetector(strategy=zscore_strategy)

    # Encryption key for alerts
    key = generate_key()

    # Run async sensor loop
    snapshots = await sensor_loop(sensors, iterations=10)  # 10 cycles

    for snapshot in snapshots:
        # Add readings to processor
        for value in snapshot.values():
            batch_ready = processor.add_reading(value)

        # Process batch if full
        if batch_ready:
            # NumPy batch processing with profiling
            (mean, std), elapsed = processor.process_batch()
            batch_data_str = ",".join(f"{v:.2f}" for v in snapshot.values())
            batch_hash = compute_sha256(batch_data_str.encode())

            print(f"Batch processed: mean={mean:.2f}, std={std:.2f}, SHA256={batch_hash}, "
                  f"time={elapsed:.6f}s")

            # Optional: Slow Python loop comparison
            (slow_mean, slow_std), slow_time = slow_process(list(snapshot.values()))
            print(f"[Slow loop] mean={slow_mean:.2f}, std={slow_std:.2f}, "
                  f"time={slow_time:.6f}s")

            # Detect anomalies
            if detector.detect(snapshot.values()):
                alert_msg = f"Anomaly detected! Mean={mean:.2f}, Std={std:.2f}"
                encrypted_alert = encrypt_alert(alert_msg, key)
                save_secure_log("alerts.log", encrypted_alert)
                decrypted_alert = decrypt_alert(encrypted_alert, key)
                print(f"Decrypted security check: {decrypted_alert}")

    # Demonstrate weakref cache
    print(f"Active sensors in cache before deletion: {cache.size()}")
    del sensors  # Remove strong references
    print(f"Active sensors in cache after deletion + GC: {cache.force_gc()}")

    print("System run completed successfully.")


# Entry Point
def main():
    asyncio.run(run_system())


if __name__ == "__main__":
    main()