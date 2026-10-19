import socket
import hashlib

def get_local_ip() -> str:
    """
    Determines the local network IP address of the current machine.
    
    Returns:
        str: The IPv4 address (e.g., '192.168.4.5').
    """
    pass

def generate_file_hash(filepath: str) -> str:
    """
    Generates a SHA-256 checksum of a file to verify integrity after transfer.
    
    Args:
        filepath (str): The absolute or relative path to the file.
        
    Returns:
        str: The hexadecimal hash string.
    """
    pass