# Secure IoT Anomaly Detection System

A secure, asynchronous IoT anomaly detection system built with advanced Python concepts, object-oriented design patterns, and secure coding practices.

---

## Features

### Architecture & Design
- Abstract Base Classes (ABC) for sensor definitions
- Factory Pattern for sensor creation
- Singleton Pattern for system configuration
- Strategy Pattern for anomaly detection algorithms
- Metaclass-based automatic sensor registration

### Asynchronous Processing
- Async sensor data collection using `asyncio`
- Concurrent execution with `asyncio.gather`
- Non-blocking sensor simulations

### Anomaly Detection
- Z-Score based statistical anomaly detection
- Threshold-based rule anomaly detection
- Runtime strategy switching

### Performance & Memory Optimization
- NumPy-based batch processing for fast computation
- Weak references for sensor cache memory safety
- Explicit garbage collection verification
- Performance comparison between NumPy and Python loops

### Security & Cryptography
- SHA-256 hashing for data integrity
- Symmetric encryption using Fernet
- Secure filename sanitization to prevent path traversal
- Safe encryption/decryption round-trip validation

---

## Project Structure

```
secure_iot_system/
├── main.py
├── requirements.txt
├── README.md
├── test_anomalies.py
├── sensor.py
├── registry.py
├── factory.py
├── config.py
├── detector.py
├── data_engine.py
├── processor.py
└── security.py
```

---

## How to Run

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the System

```bash
python main.py
```

### Run Tests

```bash
pytest -v
```

---

## Performance Proof

### NumPy vs Python Loop

The system processes sensor batches using NumPy vectorization.

- NumPy computation time is consistently faster than a manual Python loop.
- Both methods produce identical mean and standard deviation values.
- This is validated through automated unit tests.

### Profiling

A profiling decorator is applied to batch processing functions to measure execution time and identify slow operations.

---

## Memory Management Proof

- Sensors are stored using weak references.
- After deleting sensor objects and forcing garbage collection, the cache is automatically cleaned.
- Verified using `gc.collect()` and unit tests confirming cache size reaches zero.

---

## Security Validation

- SHA-256 hashes ensure data integrity before storage.
- Sensitive alerts are encrypted and decrypted using Fernet symmetric encryption.
- Filename sanitization blocks directory traversal attacks.

---

## Deployment

- A **Dockerfile** is provided to containerize the application.
- A **Kubernetes** deployment file (`deployment.yaml`) defines 3 replicas for scalable execution.

---

## Test Coverage

- 16+ pytest unit tests
- Async tests validated using `pytest-asyncio`
- All major components covered
- All tests pass successfully