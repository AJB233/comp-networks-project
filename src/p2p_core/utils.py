import socket
import hashlib
import os

def get_local_ip() -> str:
    """Finds the local IP address by opening dummy connection."""
    try:
        # We don't actually send data, just use UDP to find the preferred routing IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def generate_file_hash(filepath: str) -> str:
    """Generates a SHA-256 hash of a file for integrity checking."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()