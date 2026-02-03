# test_anomalies.py
import pytest
import asyncio
import weakref
import gc
import os
import hashlib
import numpy as np

from sensor import Sensor, TempSensor, PressureSensor, VibrationSensor
from registry import SensorRegistryMeta
from factory import SensorFactory
from config import SystemConfig
from detector import AnomalyDetector, ZScoreStrategy, ThresholdStrategy
from data_engine import sensor_loop
from processor import DataProcessor, SensorCache
from security import compute_sha256, generate_key, encrypt_alert, decrypt_alert, sanitize_filename

# OOP & Design Tests

def test_sensor_abc_instantiation():
    with pytest.raises(TypeError):
        Sensor("Abstract")  # Cannot instantiate abstract class

def test_sensor_registry_auto_register():
    registry = SensorRegistryMeta.get_registry()
    assert TempSensor in registry.values()
    assert PressureSensor in registry.values()
    assert VibrationSensor in registry.values()

def test_sensor_factory_creation():
    temp = SensorFactory.create_sensor("temperature")
    pressure = SensorFactory.create_sensor("pressure")
    vibration = SensorFactory.create_sensor("vibration")
    assert isinstance(temp, TempSensor)
    assert isinstance(pressure, PressureSensor)
    assert isinstance(vibration, VibrationSensor)

def test_systemconfig_singleton_only():
    config1 = SystemConfig()
    config2 = SystemConfig()
    assert config1 is config2  # Singleton

def test_anomaly_detector_strategy_switch_zscore():
    detector = AnomalyDetector(strategy=ZScoreStrategy(threshold=1.0))
    data = [1, 2, 3, 100]  # Definitely anomaly
    assert detector.detect(data)  # Should return True

def test_anomaly_detector_strategy_switch_threshold():
    detector = AnomalyDetector(strategy=ThresholdStrategy(min_value=0, max_value=50))
    data = [10, 20, 30, 60]  # 60 exceeds max
    assert detector.detect(data)  # Should return True

# Async Sensor Tests

import pytest_asyncio

@pytest_asyncio.fixture
async def calibrated_temp_sensor():
    sensor = TempSensor()
    sensor.calibrate()
    return sensor

@pytest.mark.asyncio
async def test_async_sensor_read_data(calibrated_temp_sensor):
    value = await calibrated_temp_sensor.read_data()
    assert isinstance(value, float)

@pytest.mark.asyncio
async def test_sensor_loop_multiple_sensors():
    sensors = [TempSensor(), PressureSensor()]
    for s in sensors:
        s.calibrate()
    snapshots = await sensor_loop(sensors, iterations=3)
    assert len(snapshots) == 3
    for snap in snapshots:
        assert all(isinstance(v, float) for v in snap.values())

# Data Processing & Memory

def test_data_processor_buffer_and_batch():
    processor = DataProcessor(batch_size=5)
    for i in range(5):
        processor.add_reading(float(i))
    (mean, std), _ = processor.process_batch()  # returns (mean,std),elapsed
    assert abs(mean - 2.0) < 1e-6
    assert abs(std - np.std([0,1,2,3,4])) < 1e-6

def test_sensor_cache_weakref():
    cache = SensorCache()
    sensor = TempSensor()
    sensor.calibrate()
    cache.add(sensor)
    assert cache.size() == 1
    del sensor
    gc.collect()
    assert cache.size() == 0

# Security & Cryptography

def test_sha256_hash():
    data = b"test_data"
    digest = compute_sha256(data)
    expected = hashlib.sha256(data).hexdigest()
    assert digest == expected

def test_encryption_round_trip():
    key = generate_key()
    message = "Critical Alert!"
    encrypted = encrypt_alert(message, key)
    decrypted = decrypt_alert(encrypted, key)
    assert decrypted == message

def test_sanitize_filename_valid():
    safe_name = sanitize_filename("log.txt")
    assert safe_name == "log.txt"

def test_sanitize_filename_blocks_traversal():
    with pytest.raises(ValueError):
        sanitize_filename("../../etc/passwd")

# Additional checks

def test_numpy_vs_slow_loop_speed():
    import time
    values = list(range(100_000))  
    # NumPy vectorized
    start_np = time.perf_counter()
    mean_np = np.mean(values)
    std_np = np.std(values)
    elapsed_np = time.perf_counter() - start_np
    # Slow Python loop
    start_py = time.perf_counter()
    mean_py = sum(values)/len(values)
    std_py = (sum((x-mean_py)**2 for x in values)/len(values))**0.5
    elapsed_py = time.perf_counter() - start_py
    assert abs(mean_np - mean_py) < 1e-6
    assert abs(std_np - std_py) < 1e-6
    assert elapsed_np < elapsed_py 

def test_sensor_cache_gc_after_multiple_adds():
    cache = SensorCache()
    sensors = [TempSensor(), PressureSensor(), VibrationSensor()]
    for s in sensors:
        s.calibrate()
        cache.add(s)
    assert cache.size() == 3

    # Delete each sensor individually
    for s in sensors:
        del s
    del sensors
    gc.collect()
    assert cache.size() == 0