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


# Hashing

def compute_sha256(data: Union[str, bytes]) -> str:
    """
    Compute a SHA-256 hash for the given data payload.
    """
    if isinstance(data, str):
        data = data.encode("utf-8")

    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


# Encryption

def generate_key() -> bytes:
    """
    Generate a new Fernet encryption key.
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


# Secure File Handling

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal attacks.

    Only plain filenames without path components are allowed.
    """
    if not filename or not filename.strip():
        raise ValueError("Filename must be a non-empty string.")

    # Reject path separators explicitly
    if (
        os.path.sep in filename
        or (os.path.altsep and os.path.altsep in filename)
    ):
        raise ValueError("Invalid filename: path separators detected.")

    sanitized = os.path.basename(filename)

    if sanitized != filename:
        raise ValueError("Invalid filename: directory traversal detected.")

    return sanitized


def save_secure_log(filename: str, data: bytes) -> None:
    """
    Safely save encrypted data to a log file.
    """
    if not isinstance(data, bytes):
        raise TypeError("Log data must be bytes.")

    safe_name = sanitize_filename(filename)

    with open(safe_name, "ab") as file:
        file.write(data + b"\n")
