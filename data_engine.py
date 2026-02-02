"""
Asynchronous data engine for sensor simulation.

This module coordinates concurrent sensor data
collection using asyncio, async/await, and generators.
"""

import asyncio
import random
from typing import List, Dict, Generator

from sensor import Sensor


def sensor_stream() -> Generator[float, None, None]:
    """
    Infinite generator simulating live sensor data.
    """
    while True:
        yield random.uniform(0.0, 100.0)


async def read_sensor(sensor: Sensor) -> float:
    """
    Read a single data point from a sensor asynchronously.
    """
    return await sensor.read_data()


async def collect_once(sensors: List[Sensor]) -> Dict[str, float]:
    """
    Collect one reading from each sensor concurrently.
    """
    tasks = [read_sensor(sensor) for sensor in sensors]
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
    snapshots = []

    for _ in range(iterations):
        snapshot = await collect_once(sensors)
        snapshots.append(snapshot)

        if delay > 0:
            await asyncio.sleep(delay)

    return snapshots