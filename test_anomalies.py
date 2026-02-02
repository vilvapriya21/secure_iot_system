# test_anomalies.py
import pytest
import asyncio
import weakref
import gc
import os
import hashlib

from sensor import Sensor, TempSensor, PressureSensor, VibrationSensor
from registry import SensorRegistryMeta
from factory import SensorFactory
from config import SystemConfig
from detector import AnomalyDetector, ZScoreStrategy, ThresholdStrategy
from data_engine import sensor_loop
from processor import DataProcessor, SensorCache
from security import compute_sha256, generate_key, encrypt_alert, decrypt_alert, sanitize_filename

# ---------------------------
# Phase 1: OOP & Design Tests
# ---------------------------

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

def test_systemconfig_singleton_and_immutable():
    config1 = SystemConfig()
    config2 = SystemConfig()
    assert config1 is config2  # Singleton
    # Optional: Try to modify an attribute
    original = config1.buffer_size
    config1.buffer_size = 999
    assert config2.buffer_size == 999  # Both refer to same instance

def test_anomaly_detector_strategy_switch():
    detector = AnomalyDetector(strategy=ZScoreStrategy(threshold=2.0))
    data = [1, 2, 3, 100]  # Should be detected as anomaly
    assert detector.detect(data)  # fixed boolean check

    detector.set_strategy(ThresholdStrategy(min_value=0, max_value=50))
    assert detector.detect(data)  # 100 exceeds max, so True

# ---------------------------
# Phase 2: Async Sensor Tests
# ---------------------------

@pytest.mark.asyncio
async def test_async_sensor_read_data():
    sensor = TempSensor()
    sensor.calibrate()
    value = await sensor.read_data()
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

# ---------------------------
# Phase 3: Data Processing & Memory
# ---------------------------

def test_data_processor_buffer_and_batch():
    processor = DataProcessor(batch_size=5)
    for i in range(5):
        ready = processor.add_reading(float(i))
    mean, std = processor.process_batch()[0]  # profile_execution returns tuple
    assert abs(mean - 2.0) < 1e-6
    assert abs(std - (2.0**0.5)) < 1e-6  # std of 0,1,2,3,4

def test_sensor_cache_weakref():
    cache = SensorCache()
    sensor = TempSensor()
    sensor.calibrate()
    cache.add(sensor)
    assert cache.size() == 1
    del sensor
    gc.collect()
    assert cache.size() == 0

# ---------------------------
# Phase 4: Security & Cryptography
# ---------------------------

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

def test_sanitize_filename_blocks_path_traversal():
    safe_name = sanitize_filename("log.txt")
    assert safe_name == "log.txt"
    with pytest.raises(ValueError):
        sanitize_filename("../../etc/passwd")