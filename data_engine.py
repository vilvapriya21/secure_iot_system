"""
Asynchronous data engine for sensor simulation.

This module coordinates concurrent sensor data
collection using asyncio, async/await, and generators.
"""

import asyncio
import random
from typing import List, Dict, Generator

from sensor import Sensor


# ---------------- Generator ---------------- #

def sensor_stream() -> Generator[float, None, None]:
    """
    Infinite generator simulating live sensor data.
    """
    while True:
        yield random.uniform(0.0, 100.0)


# ---------------- Async Readers ---------------- #

async def read_sensor(sensor: Sensor, stream: Generator[float, None, None]) -> float:
    """
    Read a single data point from a sensor asynchronously,
    pulling values from a shared generator.
    """
    await asyncio.sleep(random.uniform(0.01, 0.05))
    return next(stream)


async def collect_once(sensors: List[Sensor]) -> Dict[str, float]:
    """
    Collect one reading from each sensor concurrently.
    """
    stream = sensor_stream()

    tasks = [
        read_sensor(sensor, stream)
        for sensor in sensors
    ]

    results = await asyncio.gather(*tasks)

    return {
        sensor.name: value
        for sensor, value in zip(sensors, results)
    }


async def sensor_loop(
    sensors: List[Sensor],
    iterations: int,
    delay: float = 0.0,
) -> List[Dict[str, float]]:
    """
    Run concurrent sensor reads for a fixed number of iterations.
    """
    snapshots: List[Dict[str, float]] = []

    for _ in range(iterations):
        snapshot = await collect_once(sensors)
        snapshots.append(snapshot)

        if delay > 0:
            await asyncio.sleep(delay)

    return snapshots