"""
Security utilities for the IoT anomaly detection system.

This module provides:
- SHA-256 hashing for data integrity
- Fernet encryption for sensitive alerts
- Secure file path sanitization to prevent directory traversal
"""

import hashlib
import os
from typing import Union

from cryptography.fernet import Fernet


# ---------------- Hashing ---------------- #

def compute_sha256(data: Union[str, bytes]) -> str:
    """
    Compute a SHA-256 hash for the given data payload.

    Args:
        data: Input data as string or bytes.

    Returns:
        Hexadecimal SHA-256 hash string.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


# ---------------- Encryption ---------------- #

def generate_key() -> bytes:
    """
    Generate a new Fernet encryption key.

    Note:
        In a production system, this key should be
        securely stored and reused across sessions.
    """
    return Fernet.generate_key()


def encrypt_alert(message: str, key: bytes) -> bytes:
    """
    Encrypt a sensitive alert message.
    """
    fernet = Fernet(key)
    return fernet.encrypt(message.encode("utf-8"))


def decrypt_alert(token: bytes, key: bytes) -> str:
    """
    Decrypt an encrypted alert message.
    """
    fernet = Fernet(key)
    return fernet.decrypt(token).decode("utf-8")


# ---------------- Secure File Handling ---------------- #

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal attacks.

    Only plain filenames are allowed. Path components
    such as directories are rejected.

    Raises:
        ValueError if filename is unsafe.
    """
    if not filename or not filename.strip():
        raise ValueError("Filename must be a non-empty string.")

    sanitized = os.path.basename(filename)

    if sanitized != filename:
        raise ValueError("Invalid filename: directory traversal detected.")

    return sanitized


def save_secure_log(filename: str, data: bytes) -> None:
    """
    Safely save encrypted data to a log file.

    Appends encrypted entries as newline-delimited bytes.
    """
    if not isinstance(data, bytes):
        raise TypeError("Log data must be bytes.")

    safe_name = sanitize_filename(filename)

    with open(safe_name, "ab") as file:
        file.write(data + b"\n")